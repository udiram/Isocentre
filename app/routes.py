from collections import defaultdict
from datetime import datetime, timezone
from functools import wraps

import markdown
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .cache import public_cache
from .email_utils import (
    create_verification_token,
    email_hash,
    hash_token,
    is_mcmaster_email,
    normalize_email,
    send_verification_email,
)
from .models import (
    AdminAuditLog,
    Course,
    CourseReview,
    EmailVerificationToken,
    MentorMessage,
    MentorProfile,
    ModerationStatus,
    Notification,
    Page,
    QuestionSubmission,
    RequirementRule,
    ResourceLink,
    UserAccount,
    UserCourseStatus,
    UserSavedGuide,
)

bp = Blueprint("main", __name__)


@bp.app_context_processor
def inject_user():
    user = current_user()
    unread_notifications = 0
    unread_messages = 0
    if user:
        unread_notifications = Notification.query.filter_by(user_id=user.id, read_at=None).count()
        unread_messages = MentorMessage.query.filter_by(recipient_id=user.id, read_at=None).count()
    return {
        "current_user": user,
        "unread_notifications": unread_notifications,
        "unread_messages": unread_messages,
        "google_analytics_id": current_app.config.get("GOOGLE_ANALYTICS_ID", ""),
    }


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Sign in or create an account to use your personal dashboard.", "warning")
            return redirect(url_for("main.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def md_to_html(text):
    return markdown.markdown(text or "", extensions=["extra", "smarty"])


@bp.app_template_filter("markdown")
def markdown_filter(text):
    return md_to_html(text)


@bp.app_template_filter("tags")
def tags_filter(items):
    if not items:
        return ""
    return ", ".join(items)


@bp.app_template_filter("labelize")
def labelize_filter(value):
    return labelize(value)


@bp.route("/")
def home():
    data = public_cache.get(
        "home",
        lambda: {
            "featured_pages": Page.query.filter_by(is_featured=True).order_by(Page.section, Page.title).all(),
            "courses": Course.query.order_by(Course.level, Course.code).limit(8).all(),
            "resources": ResourceLink.query.filter_by(is_official=True).order_by(ResourceLink.category, ResourceLink.title).limit(8).all(),
            "mentors": MentorProfile.query.filter_by(status=ModerationStatus.APPROVED, featured=True)
            .order_by(MentorProfile.updated_at.desc())
            .limit(3)
            .all(),
        },
    )
    return render_template("home.html", **data)


@bp.route("/guide-map")
@bp.route("/roadmap")
def guide_map():
    data = public_cache.get(
        "guide-map",
        lambda: {
            "pages": Page.query.order_by(Page.section, Page.title).all(),
            "courses": Course.query.order_by(Course.level, Course.code).all(),
            "resources": ResourceLink.query.order_by(ResourceLink.category, ResourceLink.title).all(),
        },
    )
    grouped_pages = defaultdict(list)
    for item in data["pages"]:
        grouped_pages[item.section].append(item)
    grouped_courses = defaultdict(list)
    for course in data["courses"]:
        grouped_courses[course.level].append(course)
    return render_template(
        "guide_map.html",
        grouped_pages=grouped_pages,
        grouped_courses=grouped_courses,
        resources=data["resources"],
        roadmap=semester_roadmap(),
        faculty_contacts=research_faculty_contacts(),
        nserc=nserc_usra_guide(),
        outreach=research_outreach_template(),
        sources=roadmap_sources(),
    )


@bp.route("/search")
def search():
    query = clean_text(request.args.get("q", ""))
    pages = []
    courses_found = []
    resources_found = []
    mentors_found = []
    if query:
        like = f"%{query}%"
        normalized_like = f"%{normalize_course_code(query)}%"
        pages = (
            Page.query.filter(or_(Page.title.ilike(like), Page.summary.ilike(like), Page.body_markdown.ilike(like)))
            .order_by(Page.section, Page.title)
            .limit(12)
            .all()
        )
        courses_found = (
            Course.query.filter(
                or_(
                    Course.code.ilike(like),
                    Course.code.ilike(normalized_like),
                    Course.title.ilike(like),
                    Course.description.ilike(like),
                    Course.official_notes.ilike(like),
                )
            )
            .order_by(Course.level, Course.code)
            .limit(18)
            .all()
        )
        resources_found = (
            ResourceLink.query.filter(or_(ResourceLink.title.ilike(like), ResourceLink.category.ilike(like), ResourceLink.description.ilike(like)))
            .order_by(ResourceLink.category, ResourceLink.title)
            .limit(12)
            .all()
        )
        mentors_found = (
            MentorProfile.query.filter_by(status=ModerationStatus.APPROVED)
            .filter(or_(MentorProfile.display_name.ilike(like), MentorProfile.role_year.ilike(like), MentorProfile.bio.ilike(like)))
            .order_by(MentorProfile.featured.desc(), MentorProfile.updated_at.desc())
            .limit(8)
            .all()
        )
    return render_template(
        "search.html",
        query=query,
        pages=pages,
        courses=courses_found,
        resources=resources_found,
        mentors=mentors_found,
    )


@bp.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="img/favicon.svg"), code=302)


@bp.route("/guide/<slug>")
def page(slug):
    item = Page.query.filter_by(slug=slug).first_or_404()
    related = public_cache.get(
        f"related:{item.section}:{item.id}",
        lambda: Page.query.filter(Page.section == item.section, Page.id != item.id).order_by(Page.title).limit(4).all(),
    )
    body_html = item.body_html or md_to_html(item.body_markdown)
    return render_template("page.html", page=item, body_html=body_html, related=related)


@bp.route("/courses")
def courses():
    query = clean_text(request.args.get("q", ""))
    track = clean_text(request.args.get("track", ""))
    level = clean_text(request.args.get("level", ""))

    def load():
        course_query = Course.query
        if query:
            like = f"%{query}%"
            course_query = course_query.filter((Course.code.ilike(like)) | (Course.title.ilike(like)) | (Course.description.ilike(like)))
        if level:
            course_query = course_query.filter_by(level=int(level))
        courses = course_query.order_by(Course.level, Course.category, Course.code).all()
        if track:
            courses = [course for course in courses if track in (course.track_tags or []) or track in (course.requirement_roles or [])]
        grouped = defaultdict(list)
        for course in courses:
            grouped[course.category].append(course)
        return grouped

    grouped = load() if query or track or level else public_cache.get("courses:index", load)
    return render_template("courses.html", grouped=grouped, query=query, track=track, level=level)


@bp.route("/courses/<code>")
def course_detail(code):
    course = Course.query.filter_by(code=normalize_course_code(code)).first_or_404()
    reviews = (
        CourseReview.query.filter_by(course_id=course.id, status=ModerationStatus.APPROVED)
        .order_by(CourseReview.created_at.desc())
        .limit(12)
        .all()
    )
    review_summary = summarize_reviews(course.id)
    return render_template(
        "course_detail.html",
        course=course,
        reviews=reviews,
        review_summary=review_summary,
        pathway_links=course_pathway_links(course),
        action_plan=course_action_plan(course),
    )


@bp.route("/courses/<code>/reviews")
def course_reviews(code):
    course = Course.query.filter_by(code=normalize_course_code(code)).first_or_404()
    page_number = bounded_int(request.args.get("page"), 1, 10000, 1)
    pagination = (
        CourseReview.query.filter_by(course_id=course.id, status=ModerationStatus.APPROVED)
        .order_by(CourseReview.created_at.desc())
        .paginate(page=page_number, per_page=15, error_out=False)
    )
    return render_template(
        "course_reviews.html",
        course=course,
        reviews=pagination.items,
        pagination=pagination,
        review_summary=summarize_reviews(course.id),
    )


@bp.route("/tools/gpa")
def gpa_tool():
    return render_template("tools/gpa.html")


@bp.route("/tools/requirements")
def requirements_tool():
    rules = RequirementRule.query.order_by(RequirementRule.requirement_set, RequirementRule.sort_order, RequirementRule.label).all()
    grouped = defaultdict(list)
    for rule in rules:
        grouped[rule.requirement_set].append(rule)
    return render_template("tools/requirements.html", grouped=grouped)


@bp.route("/tools/program")
def program_tool():
    rules = RequirementRule.query.filter(RequirementRule.requirement_set != "level-ii-admission").order_by(
        RequirementRule.requirement_set, RequirementRule.sort_order
    )
    grouped = defaultdict(list)
    for rule in rules:
        grouped[rule.requirement_set].append(rule)
    return render_template(
        "tools/program.html",
        grouped=grouped,
        planner_groups=program_planner_groups(grouped),
        sample_outline=sample_course_outline(),
    )


@bp.route("/tools/cold-email")
def cold_email_tool():
    return render_template("tools/cold_email.html")


@bp.route("/sample-course-outline")
def sample_course_outline_page():
    return render_template("sample_outline.html", outline=sample_course_outline())


@bp.route("/resources")
def resources():
    grouped = public_cache.get("resources", lambda: group_resources(ResourceLink.query.order_by(ResourceLink.category, ResourceLink.title).all()))
    return render_template("resources.html", grouped=grouped)


@bp.route("/auth/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("main.dashboard"))
    if request.method == "GET":
        return render_template("auth/register.html", stages=stage_names())

    email = normalize_email(request.form.get("email", ""))
    password = request.form.get("password", "")
    display_name = clean_text(request.form.get("display_name", ""))
    stage = clean_text(request.form.get("stage", "Level I")) or "Level I"
    goal = clean_text(request.form.get("goal", ""))
    tags = split_tags(request.form.get("pathway_tags", ""))

    if not email or "@" not in email:
        flash("Enter a valid email address.", "error")
        return render_template("auth/register.html", stages=stage_names()), 400
    if not is_mcmaster_email(email):
        flash("Use your @mcmaster.ca email to create an Isocentre account.", "error")
        return render_template("auth/register.html", stages=stage_names()), 400
    if len(password) < 8:
        flash("Use a password with at least 8 characters.", "error")
        return render_template("auth/register.html", stages=stage_names()), 400
    if UserAccount.query.filter_by(email=email).first():
        flash("An account already exists for that email. Sign in instead.", "warning")
        return redirect(url_for("main.login"))

    user = UserAccount(
        email=email,
        password_hash=generate_password_hash(password),
        display_name=display_name or email.split("@", 1)[0],
        stage=stage,
        goal=goal,
        pathway_tags=tags,
        is_mcmaster=is_mcmaster_email(email),
        last_login_at=datetime.now(timezone.utc),
    )
    db.session.add(user)
    db.session.commit()
    session["user_id"] = user.id
    flash("Account created. Your dashboard is ready.", "success")
    return redirect(url_for("main.dashboard"))


@bp.route("/auth/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("main.dashboard"))
    if request.method == "GET":
        return render_template("auth/login.html")

    email = normalize_email(request.form.get("email", ""))
    password = request.form.get("password", "")
    user = UserAccount.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        flash("Invalid email or password.", "error")
        return render_template("auth/login.html"), 400
    user.last_login_at = datetime.now(timezone.utc)
    db.session.commit()
    session["user_id"] = user.id
    flash("Signed in.", "success")
    return redirect(request.args.get("next") or url_for("main.dashboard"))


@bp.route("/auth/logout")
def logout():
    session.pop("user_id", None)
    flash("Signed out.", "success")
    return redirect(url_for("main.home"))


@bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    saved_courses = (
        UserCourseStatus.query.filter_by(user_id=user.id)
        .join(Course)
        .order_by(UserCourseStatus.status, UserCourseStatus.term_label, Course.code)
        .all()
    )
    saved_guides = (
        UserSavedGuide.query.filter_by(user_id=user.id)
        .join(Page)
        .order_by(UserSavedGuide.updated_at.desc())
        .limit(8)
        .all()
    )
    completed = [item.course.code for item in saved_courses if item.status == "completed"]
    program_groups = grouped_program_results(completed)
    recommended_pages = recommended_for_stage(user.stage)
    next_courses = suggested_courses_for_stage(user.stage)
    return render_template(
        "dashboard.html",
        user=user,
        saved_courses=saved_courses,
        saved_guides=saved_guides,
        program_groups=program_groups,
        recommended_pages=recommended_pages,
        next_courses=next_courses,
        stage_flow=stage_flows().get(user.stage, []),
    )


@bp.route("/account/settings", methods=["GET", "POST"])
@login_required
def account_settings():
    user = current_user()
    mentor = (
        MentorProfile.query.filter_by(user_id=user.id)
        .order_by(MentorProfile.updated_at.desc(), MentorProfile.created_at.desc())
        .first()
    )
    if request.method == "GET":
        return render_template("auth/settings.html", user=user, stages=stage_names(), mentor=mentor)
    user.display_name = clean_text(request.form.get("display_name", user.display_name)) or user.display_name
    stage = clean_text(request.form.get("stage", user.stage)) or user.stage
    user.stage = stage if stage in stage_names() else user.stage
    user.goal = clean_text(request.form.get("goal", user.goal))
    user.pathway_tags = split_tags(request.form.get("pathway_tags", ""))

    if mentor and request.form.get("mentor_profile_present") == "yes":
        mentor.role_year = clean_text(request.form.get("mentor_role_year", mentor.role_year))[:120] or mentor.role_year
        mentor.pathway_tags = split_tags(request.form.get("mentor_pathway_tags", ""))
        mentor.experience_tags = split_tags(request.form.get("mentor_experience_tags", ""))
        mentor.bio = clean_text(request.form.get("mentor_bio", mentor.bio)) or mentor.bio
        mentor.contact_preference = clean_text(request.form.get("mentor_contact_preference", mentor.contact_preference))[:120] or mentor.contact_preference
        mentor.public_contact_text = clean_text(request.form.get("mentor_public_contact_text", mentor.public_contact_text))[:240]
        mentor.mentorship_available = request.form.get("mentor_available", "yes") == "yes"
        visibility = request.form.get("mentor_visibility", "visible")
        if visibility == "hidden":
            mentor.status = ModerationStatus.HIDDEN
        elif mentor.status == ModerationStatus.HIDDEN:
            mentor.status = ModerationStatus.PENDING
            mentor.moderated_at = None
        db.session.add(mentor)
        public_cache.clear()

    db.session.commit()
    flash("Account settings updated.", "success")
    return redirect(url_for("main.dashboard"))


@bp.route("/planner", methods=["GET", "POST"])
@login_required
def planner():
    user = current_user()
    courses = Course.query.order_by(Course.level, Course.code).all()
    if request.method == "POST":
        course = Course.query.filter_by(code=normalize_course_code(request.form.get("course_code", ""))).first_or_404()
        item = UserCourseStatus.query.filter_by(user_id=user.id, course_id=course.id).first()
        if not item:
            item = UserCourseStatus(user_id=user.id, course_id=course.id)
            db.session.add(item)
        item.status = request.form.get("status", "planned") if request.form.get("status") in course_statuses() else "planned"
        item.term_label = clean_text(request.form.get("term_label", ""))
        item.note = clean_text(request.form.get("note", ""))
        db.session.commit()
        flash(f"{course.code} saved to your planner.", "success")
        return redirect(url_for("main.planner"))
    saved = (
        UserCourseStatus.query.filter_by(user_id=user.id)
        .join(Course)
        .order_by(UserCourseStatus.status, UserCourseStatus.term_label, Course.code)
        .all()
    )
    return render_template("planner.html", courses=courses, saved=saved, statuses=course_statuses())


@bp.route("/planner/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_planner_item(item_id):
    item = UserCourseStatus.query.filter_by(id=item_id, user_id=current_user().id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash("Removed from your planner.", "success")
    return redirect(request.referrer or url_for("main.planner"))


@bp.route("/courses/<code>/save", methods=["POST"])
@login_required
def save_course(code):
    course = Course.query.filter_by(code=normalize_course_code(code)).first_or_404()
    status = request.form.get("status", "interested")
    if status not in course_statuses():
        status = "interested"
    item = UserCourseStatus.query.filter_by(user_id=current_user().id, course_id=course.id).first()
    if not item:
        item = UserCourseStatus(user_id=current_user().id, course_id=course.id)
        db.session.add(item)
    item.status = status
    item.term_label = clean_text(request.form.get("term_label", item.term_label))
    db.session.commit()
    flash(f"{course.code} saved.", "success")
    return redirect(request.referrer or url_for("main.course_detail", code=course.code))


@bp.route("/guide/<slug>/save", methods=["POST"])
@login_required
def save_guide(slug):
    page_item = Page.query.filter_by(slug=slug).first_or_404()
    saved = UserSavedGuide.query.filter_by(user_id=current_user().id, page_id=page_item.id).first()
    if not saved:
        db.session.add(UserSavedGuide(user_id=current_user().id, page_id=page_item.id))
        db.session.commit()
        flash("Guide saved to your dashboard.", "success")
    else:
        flash("This guide is already on your dashboard.", "warning")
    return redirect(request.referrer or url_for("main.page", slug=slug))


@bp.route("/notifications")
@login_required
def notifications():
    user = current_user()
    items = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(80).all()
    messages = MentorMessage.query.filter_by(recipient_id=user.id).order_by(MentorMessage.created_at.desc()).limit(10).all()
    return render_template("notifications.html", notifications=items, messages=messages)


@bp.route("/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    item = Notification.query.filter_by(id=notification_id, user_id=current_user().id).first_or_404()
    item.read_at = item.read_at or datetime.now(timezone.utc)
    db.session.commit()
    return redirect(item.link_url or url_for("main.notifications"))


@bp.route("/notifications/read-all", methods=["POST"])
@login_required
def mark_all_notifications_read():
    now = datetime.now(timezone.utc)
    Notification.query.filter_by(user_id=current_user().id, read_at=None).update({"read_at": now})
    db.session.commit()
    flash("Notifications marked as read.", "success")
    return redirect(url_for("main.notifications"))


@bp.route("/messages")
@login_required
def messages():
    user = current_user()
    inbox = MentorMessage.query.filter_by(recipient_id=user.id).order_by(MentorMessage.created_at.desc()).all()
    sent = MentorMessage.query.filter_by(sender_id=user.id).order_by(MentorMessage.created_at.desc()).limit(40).all()
    return render_template("messages.html", inbox=inbox, sent=sent)


@bp.route("/messages/<int:message_id>")
@login_required
def message_detail(message_id):
    user = current_user()
    message = MentorMessage.query.filter(
        MentorMessage.id == message_id,
        or_(MentorMessage.recipient_id == user.id, MentorMessage.sender_id == user.id),
    ).first_or_404()
    if message.recipient_id == user.id and not message.read_at:
        message.read_at = datetime.now(timezone.utc)
        Notification.query.filter_by(
            user_id=user.id, target_type="MentorMessage", target_id=message.id, read_at=None
        ).update({"read_at": message.read_at})
        db.session.commit()
    return render_template("message_detail.html", message=message)


@bp.route("/community")
def community():
    user = current_user()
    mentors_query = MentorProfile.query.filter_by(status=ModerationStatus.APPROVED)
    mentors = (
        mentors_query
        .order_by(MentorProfile.featured.desc(), MentorProfile.mentorship_available.desc(), MentorProfile.updated_at.desc())
        .limit(6)
        .all()
    )
    matching_mentors = mentor_matches_for_user(user, limit=6) if user else []
    stats = {
        "mentors": mentors_query.count(),
        "available_mentors": mentors_query.filter_by(mentorship_available=True).count(),
        "dm_mentors": mentors_query.filter(MentorProfile.user_id.isnot(None)).count(),
        "reviews": CourseReview.query.filter_by(status=ModerationStatus.APPROVED).count(),
    }
    recent_reviews = (
        CourseReview.query.filter_by(status=ModerationStatus.APPROVED)
        .order_by(CourseReview.created_at.desc())
        .limit(6)
        .all()
    )
    return render_template(
        "community.html",
        mentors=mentors,
        matching_mentors=matching_mentors,
        recent_reviews=recent_reviews,
        stats=stats,
        upper_year_count=len(higher_year_users(user)) if user else 0,
    )


@bp.route("/community/mentors")
def mentors():
    tag = clean_text(request.args.get("tag", ""))
    query = clean_text(request.args.get("q", ""))
    availability = clean_text(request.args.get("availability", "available"))
    contact = clean_text(request.args.get("contact", "any"))
    page_number = bounded_int(request.args.get("page"), 1, 10000, 1)
    all_mentors = (
        MentorProfile.query.filter_by(status=ModerationStatus.APPROVED)
        .order_by(MentorProfile.featured.desc(), MentorProfile.mentorship_available.desc(), MentorProfile.updated_at.desc())
        .all()
    )
    mentors = filter_mentors(all_mentors, query=query, tag=tag, availability=availability, contact=contact)
    pagination = paginate_list(mentors, page_number, 12)
    suggested_tags = mentor_tag_cloud(all_mentors)
    return render_template(
        "mentors.html",
        mentors=pagination.items,
        tag=tag,
        query=query,
        availability=availability,
        contact=contact,
        pagination=pagination,
        suggested_tags=suggested_tags,
        total_matches=len(mentors),
    )


@bp.route("/community/ask")
@login_required
def ask_upper_year():
    user = current_user()
    return render_template("ask.html", upper_year_count=len(higher_year_users(user)), sample_topics=question_starter_topics(user))


@bp.route("/submit/review", methods=["GET", "POST"])
@login_required
def submit_review():
    user = current_user()
    courses = Course.query.order_by(Course.code).all()
    if request.method == "GET":
        selected = normalize_course_code(request.args.get("course", ""))
        return render_template("submit_review.html", courses=courses, selected=selected)

    email = normalize_email(user.email)

    course = Course.query.filter_by(code=normalize_course_code(request.form.get("course_code", ""))).first_or_404()
    review = CourseReview(
        course=course,
        user_id=user.id,
        email_private=email,
        submitter_email_hash=email_hash(email),
        status=ModerationStatus.PENDING,
        term_taken=clean_text(request.form.get("term_taken", "Not specified")),
        difficulty=bounded_int(request.form.get("difficulty"), 1, 5, 3),
        workload=bounded_int(request.form.get("workload"), 1, 5, 3),
        usefulness=bounded_int(request.form.get("usefulness"), 1, 5, 3),
        math_intensity=bounded_int(request.form.get("math_intensity"), 1, 5, 3),
        coding_intensity=bounded_int(request.form.get("coding_intensity"), 1, 5, 1),
        memorization_intensity=bounded_int(request.form.get("memorization_intensity"), 1, 5, 2),
        would_take_again=request.form.get("would_take_again") == "yes",
        advice=clean_text(request.form.get("advice", "")),
    )
    db.session.add(review)
    db.session.flush()
    notify_user(
        user.id,
        "Course review submitted",
        f"Your review for {course.code} is in the moderation queue.",
        "review",
        url_for("main.course_reviews", code=course.code),
        target_type="CourseReview",
        target_id=review.id,
    )
    db.session.commit()
    flash("Review submitted to moderation. You can track updates in notifications.", "success")
    return redirect(url_for("main.course_detail", code=course.code))


@bp.route("/submit/mentor", methods=["GET", "POST"])
@login_required
def submit_mentor():
    user = current_user()
    if request.method == "GET":
        return render_template("submit_mentor.html")

    email = normalize_email(user.email)

    mentor = MentorProfile(
        user_id=user.id,
        display_name=clean_text(request.form.get("display_name", "Anonymous mentor")),
        role_year=clean_text(request.form.get("role_year", "MedBioPhys student/alum")),
        pathway_tags=split_tags(request.form.get("pathway_tags", "")),
        experience_tags=split_tags(request.form.get("experience_tags", "")),
        bio=clean_text(request.form.get("bio", "")),
        contact_preference=clean_text(request.form.get("contact_preference", "Ask through public contact text")),
        public_contact_text=clean_text(request.form.get("public_contact_text", "")),
        private_email=email,
        email_hash=email_hash(email),
        status=ModerationStatus.PENDING,
        mentorship_available=request.form.get("mentorship_available") == "yes",
    )
    db.session.add(mentor)
    db.session.flush()
    notify_user(
        user.id,
        "Mentor profile submitted",
        "Your mentor profile is in the moderation queue.",
        "mentor",
        url_for("main.mentors"),
        target_type="MentorProfile",
        target_id=mentor.id,
    )
    db.session.commit()
    flash("Mentor profile submitted to moderation. You will see updates in notifications.", "success")
    return redirect(url_for("main.community"))


@bp.route("/community/ask", methods=["POST"])
@login_required
def submit_question():
    user = current_user()
    email = normalize_email(user.email)
    body = clean_text(request.form.get("body", ""))
    if not body:
        flash("Write your question before sending it to upper-years.", "error")
        return render_template("ask.html"), 400

    question = QuestionSubmission(
        user_id=user.id,
        stage=user.stage,
        topic=clean_text(request.form.get("topic", "General question")),
        body=body,
        private_email=email,
        email_hash=email_hash(email),
        status=ModerationStatus.PENDING,
    )
    db.session.add(question)
    db.session.flush()
    notify_user(
        user.id,
        "Question submitted",
        f"Your question about {question.topic} is in the moderation queue.",
        "question",
        url_for("main.community"),
        target_type="QuestionSubmission",
        target_id=question.id,
    )
    recipients = notify_higher_years(question, user)
    db.session.commit()
    flash(f"Question sent to {recipients} higher-year student{'s' if recipients != 1 else ''}. Replies appear in your notifications.", "success")
    return redirect(url_for("main.question_detail", question_id=question.id))


@bp.route("/community/ask/<int:question_id>", methods=["GET", "POST"])
@login_required
def question_detail(question_id):
    user = current_user()
    question = db.session.get(QuestionSubmission, question_id)
    if not question:
        abort(404)
    if not can_view_question(user, question):
        abort(403)

    asker = question.user
    if request.method == "POST":
        if user.id == question.user_id:
            flash("You cannot answer your own question.", "warning")
            return redirect(url_for("main.question_detail", question_id=question.id))
        response = clean_text(request.form.get("response", ""))
        if not response:
            flash("Write a response before sending it.", "error")
            return render_template("question_detail.html", question=question, asker=asker, can_reply=True), 400
        notify_user(
            question.user_id,
            "New upper-year response",
            f"{user.display_name} ({user.stage}) replied to your question about {question.topic}: {response}",
            "question-reply",
            url_for("main.question_detail", question_id=question.id),
            actor_label=user.display_name,
            target_type="QuestionSubmission",
            target_id=question.id,
        )
        db.session.commit()
        flash("Response sent to the asker’s notifications.", "success")
        return redirect(url_for("main.question_detail", question_id=question.id))

    return render_template("question_detail.html", question=question, asker=asker, can_reply=user.id != question.user_id)


@bp.route("/community/mentors/<int:mentor_id>/message", methods=["GET", "POST"])
@login_required
def message_mentor(mentor_id):
    mentor = MentorProfile.query.filter_by(id=mentor_id, status=ModerationStatus.APPROVED).first_or_404()
    if not mentor.user_id:
        flash("This mentor has not connected an inbox yet.", "warning")
        return redirect(url_for("main.mentors"))
    user = current_user()
    if mentor.user_id == user.id:
        flash("This is your own mentor profile.", "warning")
        return redirect(url_for("main.mentors"))
    if request.method == "GET":
        return render_template("message_mentor.html", mentor=mentor)
    subject = clean_text(request.form.get("subject", "Mentorship question"))
    body = clean_text(request.form.get("body", ""))
    if not body:
        flash("Write a short message before sending.", "error")
        return render_template("message_mentor.html", mentor=mentor), 400
    message = MentorMessage(
        mentor_id=mentor.id,
        sender_id=user.id,
        recipient_id=mentor.user_id,
        subject=subject,
        body=body,
    )
    db.session.add(message)
    db.session.flush()
    notify_user(
        mentor.user_id,
        "New mentor message",
        f"{user.display_name} sent you a question: {subject}",
        "message",
        url_for("main.message_detail", message_id=message.id),
        actor_label=user.display_name,
        target_type="MentorMessage",
        target_id=message.id,
    )
    db.session.commit()
    flash("Message sent. The mentor will see it in their Isocentre inbox.", "success")
    return redirect(url_for("main.mentors"))


@bp.route("/verify-email/<token>")
def verify_email(token):
    record = EmailVerificationToken.query.filter_by(token_hash=hash_token(token)).first_or_404()
    now = datetime.now(timezone.utc)
    if record.consumed_at:
        flash("This verification link has already been used.", "warning")
        return redirect(url_for("main.community"))
    if record.expires_at.replace(tzinfo=timezone.utc) < now:
        flash("This verification link expired. Please submit again.", "error")
        return redirect(url_for("main.community"))

    target = get_moderated_target(record.target_type, record.target_id)
    target.status = ModerationStatus.PENDING
    target.verified_at = now
    record.consumed_at = now
    db.session.add(AdminAuditLog(action="verify", target_type=record.target_type, target_id=record.target_id, detail=record.email))
    db.session.commit()
    flash("Email verified. Your submission is now waiting for moderation.", "success")
    return redirect(url_for("main.community"))


@bp.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if current_app.config.get("ADMIN_PASSWORD") and request.form.get("password") == current_app.config["ADMIN_PASSWORD"]:
            session["admin"] = True
            return redirect(url_for("main.admin"))
        flash("Invalid admin password.", "error")
    if not is_admin():
        return render_template("admin_login.html")
    counts = {
        "pending_reviews": CourseReview.query.filter_by(status=ModerationStatus.PENDING).count(),
        "pending_mentors": MentorProfile.query.filter_by(status=ModerationStatus.PENDING).count(),
        "pending_questions": QuestionSubmission.query.filter_by(status=ModerationStatus.PENDING).count(),
        "approved_reviews": CourseReview.query.filter_by(status=ModerationStatus.APPROVED).count(),
        "approved_mentors": MentorProfile.query.filter_by(status=ModerationStatus.APPROVED).count(),
        "users": UserAccount.query.count(),
        "messages": MentorMessage.query.count(),
        "notifications": Notification.query.count(),
        "pages": Page.query.count(),
        "courses": Course.query.count(),
    }
    recent = {
        "reviews": CourseReview.query.order_by(CourseReview.created_at.desc()).limit(5).all(),
        "mentors": MentorProfile.query.order_by(MentorProfile.created_at.desc()).limit(5).all(),
        "questions": QuestionSubmission.query.order_by(QuestionSubmission.created_at.desc()).limit(5).all(),
        "users": UserAccount.query.order_by(UserAccount.created_at.desc()).limit(5).all(),
    }
    return render_template("admin.html", counts=counts, recent=recent)


@bp.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("main.home"))


@bp.route("/admin/reviews")
def admin_reviews():
    require_admin()
    status = clean_text(request.args.get("status", "pending"))
    query = clean_text(request.args.get("q", ""))
    page_number = bounded_int(request.args.get("page"), 1, 10000, 1)
    review_query = CourseReview.query.join(Course)
    if status and status != "all":
        review_query = review_query.filter(CourseReview.status == status)
    if query:
        like = f"%{query}%"
        review_query = review_query.filter((Course.code.ilike(like)) | (CourseReview.email_private.ilike(like)) | (CourseReview.advice.ilike(like)))
    pagination = review_query.order_by(CourseReview.status, CourseReview.created_at.desc()).paginate(page=page_number, per_page=25, error_out=False)
    return render_template("admin_reviews.html", reviews=pagination.items, pagination=pagination, status=status, query=query)


@bp.route("/admin/mentors")
def admin_mentors():
    require_admin()
    status = clean_text(request.args.get("status", "pending"))
    query = clean_text(request.args.get("q", ""))
    page_number = bounded_int(request.args.get("page"), 1, 10000, 1)
    mentor_query = MentorProfile.query
    if status and status != "all":
        mentor_query = mentor_query.filter(MentorProfile.status == status)
    if query:
        like = f"%{query}%"
        mentor_query = mentor_query.filter(
            (MentorProfile.display_name.ilike(like)) | (MentorProfile.private_email.ilike(like)) | (MentorProfile.bio.ilike(like))
        )
    pagination = mentor_query.order_by(MentorProfile.status, MentorProfile.created_at.desc()).paginate(
        page=page_number, per_page=25, error_out=False
    )
    return render_template("admin_mentors.html", mentors=pagination.items, pagination=pagination, status=status, query=query)


@bp.route("/admin/mentors/new", methods=["GET", "POST"])
def admin_mentor_new():
    require_admin()
    mentor = MentorProfile(
        display_name="",
        role_year="",
        pathway_tags=[],
        experience_tags=[],
        bio="",
        contact_preference="Isocentre inbox",
        public_contact_text="",
        private_email="",
        email_hash="",
        status=ModerationStatus.APPROVED,
        mentorship_available=True,
        featured=False,
    )
    if request.method == "POST":
        if save_admin_mentor_form(mentor):
            db.session.add(mentor)
            db.session.flush()
            db.session.add(AdminAuditLog(action="create", target_type="MentorProfile", target_id=mentor.id))
            db.session.commit()
            public_cache.clear()
            flash("Mentor profile created.", "success")
            return redirect(url_for("main.admin_mentors", status="all"))
        db.session.rollback()
    return render_template("admin_mentor_form.html", mentor=mentor, mode="new", users=mentor_owner_options())


@bp.route("/admin/mentors/<int:mentor_id>/edit", methods=["GET", "POST"])
def admin_mentor_edit(mentor_id):
    require_admin()
    mentor = db.session.get(MentorProfile, mentor_id)
    if not mentor:
        abort(404)
    if request.method == "POST":
        if save_admin_mentor_form(mentor):
            db.session.add(AdminAuditLog(action="edit", target_type="MentorProfile", target_id=mentor.id))
            db.session.commit()
            public_cache.clear()
            flash("Mentor profile updated.", "success")
            return redirect(url_for("main.admin_mentors", status="all", q=mentor.display_name))
        db.session.rollback()
    return render_template("admin_mentor_form.html", mentor=mentor, mode="edit", users=mentor_owner_options())


@bp.route("/admin/questions")
def admin_questions():
    require_admin()
    status = clean_text(request.args.get("status", "pending"))
    query = clean_text(request.args.get("q", ""))
    page_number = bounded_int(request.args.get("page"), 1, 10000, 1)
    question_query = QuestionSubmission.query
    if status and status != "all":
        question_query = question_query.filter(QuestionSubmission.status == status)
    if query:
        like = f"%{query}%"
        question_query = question_query.filter(
            (QuestionSubmission.topic.ilike(like)) | (QuestionSubmission.private_email.ilike(like)) | (QuestionSubmission.body.ilike(like))
        )
    pagination = question_query.order_by(QuestionSubmission.status, QuestionSubmission.created_at.desc()).paginate(
        page=page_number, per_page=25, error_out=False
    )
    return render_template("admin_questions.html", questions=pagination.items, pagination=pagination, status=status, query=query)


@bp.route("/admin/users")
def admin_users():
    require_admin()
    query = clean_text(request.args.get("q", ""))
    page_number = bounded_int(request.args.get("page"), 1, 10000, 1)
    user_query = UserAccount.query
    if query:
        like = f"%{query}%"
        user_query = user_query.filter(
            or_(UserAccount.email.ilike(like), UserAccount.display_name.ilike(like), UserAccount.stage.ilike(like), UserAccount.goal.ilike(like))
        )
    pagination = user_query.order_by(UserAccount.created_at.desc()).paginate(page=page_number, per_page=30, error_out=False)
    return render_template("admin_users.html", users=pagination.items, pagination=pagination, query=query)


@bp.route("/admin/messages")
def admin_messages():
    require_admin()
    query = clean_text(request.args.get("q", ""))
    page_number = bounded_int(request.args.get("page"), 1, 10000, 1)
    message_query = MentorMessage.query
    if query:
        like = f"%{query}%"
        message_query = message_query.filter(or_(MentorMessage.subject.ilike(like), MentorMessage.body.ilike(like)))
    pagination = message_query.order_by(MentorMessage.created_at.desc()).paginate(page=page_number, per_page=30, error_out=False)
    return render_template("admin_messages.html", messages=pagination.items, pagination=pagination, query=query)


@bp.route("/admin/pages")
def admin_pages():
    require_admin()
    pages = Page.query.order_by(Page.section, Page.title).all()
    courses = Course.query.order_by(Course.level, Course.code).all()
    return render_template("admin_pages.html", pages=pages, courses=courses)


@bp.route("/admin/moderate/<target_type>/<int:target_id>/<action>", methods=["POST"])
def admin_moderate(target_type, target_id, action):
    require_admin()
    if action not in {"approve", "reject", "hide", "feature", "unfeature"}:
        abort(400)
    target = get_moderated_target(target_type, target_id)
    now = datetime.now(timezone.utc)
    if action == "approve":
        target.status = ModerationStatus.APPROVED
    elif action == "reject":
        target.status = ModerationStatus.REJECTED
    elif action == "hide":
        target.status = ModerationStatus.HIDDEN
    elif action == "feature" and hasattr(target, "featured"):
        target.featured = True
    elif action == "unfeature" and hasattr(target, "featured"):
        target.featured = False
    target.moderated_at = now
    db.session.add(AdminAuditLog(action=action, target_type=target_type, target_id=target_id))
    notify_moderation_result(target, target_type, action)
    if target_type == "CourseReview" and action == "approve":
        notify_course_review_followers(target)
    db.session.commit()
    public_cache.clear()
    return redirect(request.referrer or url_for("main.admin"))


@bp.route("/admin/delete/<target_type>/<int:target_id>", methods=["POST"])
def admin_delete(target_type, target_id):
    require_admin()
    if target_type == "UserAccount":
        target = db.session.get(UserAccount, target_id)
        if not target:
            abort(404)
        delete_user_account(target)
        db.session.commit()
        public_cache.clear()
        flash("User account and related community activity deleted.", "success")
        return redirect(request.referrer or url_for("main.admin_users"))
    if target_type == "MentorMessage":
        target = db.session.get(MentorMessage, target_id)
        if not target:
            abort(404)
        delete_mentor_message(target)
        db.session.commit()
        flash("Mentor message deleted.", "success")
        return redirect(request.referrer or url_for("main.admin_messages"))
    if target_type == "MentorProfile":
        target = db.session.get(MentorProfile, target_id)
        if not target:
            abort(404)
        message_ids = [row.id for row in MentorMessage.query.with_entities(MentorMessage.id).filter_by(mentor_id=target.id).all()]
        if message_ids:
            Notification.query.filter(Notification.target_type == "MentorMessage", Notification.target_id.in_(message_ids)).delete(
                synchronize_session=False
            )
        MentorMessage.query.filter_by(mentor_id=target.id).delete(synchronize_session=False)
    else:
        target = get_moderated_target(target_type, target_id)

    Notification.query.filter_by(target_type=target_type, target_id=target_id).delete(synchronize_session=False)
    db.session.add(AdminAuditLog(action="delete", target_type=target_type, target_id=target_id, detail=getattr(target, "display_name", "")))
    db.session.delete(target)
    db.session.commit()
    public_cache.clear()
    flash(f"{labelize(target_type)} deleted.", "success")
    if target_type == "MentorProfile":
        return redirect(url_for("main.admin_mentors", status="all"))
    return redirect(request.referrer or url_for("main.admin"))


@bp.route("/api/requirements/check", methods=["POST"])
def check_requirements():
    payload = request.get_json(silent=True) or {}
    completed = {normalize_course_code(code) for code in payload.get("courses", []) if str(code).strip()}
    requirement_set = payload.get("requirement_set", "level-ii-admission")
    rules = RequirementRule.query.filter_by(requirement_set=requirement_set).order_by(RequirementRule.sort_order, RequirementRule.label).all()
    return jsonify({"results": [evaluate_rule(rule, completed) for rule in rules]})


@bp.route("/api/program/check", methods=["POST"])
def check_program():
    payload = request.get_json(silent=True) or {}
    completed = {normalize_course_code(code) for code in payload.get("courses", []) if str(code).strip()}
    rules = RequirementRule.query.filter(RequirementRule.requirement_set != "level-ii-admission").order_by(
        RequirementRule.requirement_set, RequirementRule.sort_order
    )
    grouped = defaultdict(list)
    for rule in rules:
        grouped[rule.requirement_set].append(evaluate_rule(rule, completed))
    return jsonify({"groups": grouped})


@bp.route("/api/cold-email", methods=["POST"])
def cold_email():
    payload = request.get_json(silent=True) or {}
    purpose = payload.get("purpose", "research")
    name = clean_text(payload.get("name", "Your Name"))
    recipient = clean_text(payload.get("recipient", "Professor"))
    interests = clean_text(payload.get("interests", "medical and biological physics"))
    experience = clean_text(payload.get("experience", "coursework, coding, and lab experience"))
    ask = clean_text(payload.get("ask", "a short meeting to ask whether there may be a fit"))
    tone = payload.get("tone", "direct")

    if purpose not in {"research", "coop", "grad"}:
        abort(400, "Unsupported email purpose.")

    subject_map = {
        "research": f"Undergraduate research inquiry - {interests}",
        "coop": f"Co-op inquiry - {interests}",
        "grad": f"Prospective graduate student inquiry - {interests}",
    }
    context_map = {
        "research": "I am an undergraduate student exploring research opportunities in Medical and Biological Physics.",
        "coop": "I am preparing for co-op roles that connect physics, computation, imaging, and health science.",
        "grad": "I am exploring graduate programs and supervisors whose work connects with my interests.",
    }
    tone_line = "I will keep this brief." if tone == "direct" else "I hope your week is going well."

    body = f"""Subject: {subject_map[purpose]}

Dear {recipient},

{tone_line} {context_map[purpose]} I am especially interested in {interests}.

My relevant background includes {experience}. I am looking for {ask}, and I would be grateful to learn whether there is a reasonable fit or whether you would suggest another person or resource.

I have attached or linked a resume/transcript/project summary where appropriate. Thank you for your time.

Best,
{name}"""

    return jsonify({"subject": subject_map[purpose], "body": body})


def evaluate_rule(rule, completed):
    groups = normalize_option_groups(rule.course_options)
    matched_groups = [group for group in groups if any(code in completed for code in group)]
    matched_units = len(matched_groups) * rule.option_units
    required_units = rule.units_required or (rule.required_count * rule.option_units)

    if rule.rule_type == "advisor":
        status = "check-advisor"
    elif not groups:
        status = "check-advisor"
    elif rule.rule_type == "all":
        status = "complete" if len(matched_groups) == len(groups) else ("check-advisor" if matched_groups else "missing")
    elif matched_units >= required_units:
        status = "complete"
    elif matched_groups:
        status = "check-advisor"
    else:
        status = "missing"

    return {
        "code": rule.code,
        "label": rule.label,
        "description": rule.description,
        "status": status,
        "matched": sorted({course for group in matched_groups for course in group if course in completed}),
        "matched_units": matched_units,
        "required_units": required_units,
        "track": rule.track,
        "note": rule.advisory_note,
    }


def normalize_option_groups(options):
    groups = []
    for item in options or []:
        if isinstance(item, list):
            groups.append([normalize_course_code(code) for code in item])
        else:
            groups.append([normalize_course_code(item)])
    return groups


def summarize_reviews(course_id):
    reviews = CourseReview.query.filter_by(course_id=course_id, status=ModerationStatus.APPROVED).all()
    if not reviews:
        return None
    fields = ["difficulty", "workload", "usefulness", "math_intensity", "coding_intensity", "memorization_intensity"]
    return {
        "count": len(reviews),
        "would_take_again": round(100 * sum(1 for review in reviews if review.would_take_again) / len(reviews)),
        **{field: round(sum(getattr(review, field) for review in reviews) / len(reviews), 1) for field in fields},
    }


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(UserAccount, user_id)


def grouped_program_results(completed_codes):
    completed = {normalize_course_code(code) for code in completed_codes}
    rules = RequirementRule.query.filter(RequirementRule.requirement_set != "level-ii-admission").order_by(
        RequirementRule.requirement_set, RequirementRule.sort_order
    )
    grouped = defaultdict(list)
    for rule in rules:
        grouped[rule.requirement_set].append(evaluate_rule(rule, completed))
    return grouped


def stage_names():
    return ["Prospective", "Level I", "Level II", "Upper-year", "Graduating", "Alumni"]


def course_statuses():
    return ["interested", "planned", "in-progress", "completed"]


def stage_flows():
    return {
        "Prospective": [
            ("Compare MedBioPhys vs MRSc", "medbiophys-vs-mrsc"),
            ("Understand the program", "medbiophys-explained"),
            ("Check Level I gateways", "level-ii-admission-guide"),
        ],
        "Level I": [
            ("Protect admission requirements", "level-ii-admission-guide"),
            ("Compare course paths", "level-ii-survival-guide"),
            ("Start a lightweight coding/research portfolio", "research-guide"),
        ],
        "Level II": [
            ("Use the physics shock-year guide", "level-ii-survival-guide"),
            ("Add core courses to planner", "upper-year-planning"),
            ("Start research outreach", "research-guide"),
        ],
        "Upper-year": [
            ("Choose a Course List track", "upper-year-planning"),
            ("Plan thesis or senior project", "thesis-and-senior-project-guide"),
            ("Map career pathway", "career-pathways"),
        ],
        "Graduating": [
            ("CAMPEP and grad timeline", "grad-school-campep-guide"),
            ("Clinical pathway reality check", "clinical-medical-physics-roadmap"),
            ("Use cold email templates", "cold-email-templates"),
        ],
        "Alumni": [
            ("Join the mentor directory", "course-review-guidelines"),
            ("Share course reviews", "level-ii-survival-guide"),
            ("Help students compare pathways", "career-pathways"),
        ],
    }


def recommended_for_stage(stage):
    slugs = [slug for _, slug in stage_flows().get(stage, stage_flows()["Level I"])]
    return Page.query.filter(Page.slug.in_(slugs)).order_by(Page.section, Page.title).all()


def suggested_courses_for_stage(stage):
    by_stage = {
        "Prospective": ["MEDPHYS1A03", "PHYSICS1A03", "PHYSICS1AA3", "MATH1A03"],
        "Level I": ["PHYSICS1A03", "PHYSICS1AA3", "MATH1A03", "MATH1AA3", "CHEM1A03", "BIOLOGY1A03"],
        "Level II": ["PHYSICS2C03", "PHYSICS2P03", "PHYSICS2G03", "MATH2C03", "BIOPHYS2S03"],
        "Upper-year": ["MEDPHYS4B03", "MEDPHYS4D03", "MEDPHYS4T03", "BIOPHYS4S03", "PHYSICS4P06"],
        "Graduating": ["MEDPHYS4Y06", "PHYSICS4G03", "MEDPHYS4U03", "MEDPHYS4F03"],
        "Alumni": ["PHYSICS2G03", "MEDPHYS4D03", "MEDPHYS4T03"],
    }
    return Course.query.filter(Course.code.in_(by_stage.get(stage, by_stage["Level II"]))).order_by(Course.level, Course.code).all()


def course_pathway_links(course):
    tags = set(course.track_tags or []) | set(course.requirement_roles or [])
    links = []
    if "medical-physics" in tags or "clinical" in tags or "course-list-a" in tags:
        links.append(("Clinical medical physics", "clinical-medical-physics-roadmap"))
    if "health-physics" in tags or "radiation-safety" in tags:
        links.append(("Health physics", "health-physics-radiation-protection"))
    if "data-ai" in tags or "imaging" in tags:
        links.append(("Imaging / AI portfolio", "medical-imaging-ai-portfolio"))
    if "research" in tags or "grad-school" in tags:
        links.append(("Research and thesis", "research-guide"))
        links.append(("Thesis guide", "thesis-and-senior-project-guide"))
    if "biological-physics" in tags or "wet-lab" in tags:
        links.append(("Biophysics pathway", "upper-year-planning"))
    if "soft-matter" in tags:
        links.append(("Soft matter planning", "upper-year-planning"))
    if course.level <= 2:
        links.append(("Level II survival", "level-ii-survival-guide"))
    deduped = []
    seen = set()
    for title, slug in links:
        if slug not in seen:
            deduped.append((title, slug))
            seen.add(slug)
    return deduped[:5]


def course_action_plan(course):
    tags = set(course.track_tags or []) | set(course.requirement_roles or [])
    plan = []
    if course.level <= 1:
        plan.append("Use this course to protect Level II admission options, then check whether it also satisfies a recommended preparation note.")
    if "level-ii-required" in tags or course.level == 2:
        plan.append("Add it to your Level II workload map and decide which weekly habit it needs: problem sets, lab reports, coding, or memorization.")
    if "course-list-a" in tags or "medical-physics" in tags:
        plan.append("If you are clinical/health-physics curious, save one artifact from this course that shows radiation, imaging, anatomy, or safety reasoning.")
    if "data-ai" in tags:
        plan.append("Turn one assignment or concept into a clean notebook, figure, or mini-project that can support research/co-op outreach.")
    if "research" in tags or "grad-school" in tags:
        plan.append("Ask how this course could connect to a thesis, summer project, supervisor email, poster, or graduate-school statement.")
    if "biological-physics" in tags or "soft-matter" in tags:
        plan.append("Write down the physical model and the biological/material system together; this is how the course becomes useful later.")
    if not plan:
        plan.append("Use the course to fill a requirement deliberately, then connect it to one pathway, skill, or future course before registration.")
    plan.append("Before enrolling, verify prerequisites, antirequisites, term offering, and your calendar year using official McMaster sources.")
    return plan[:5]


def semester_roadmap():
    return [
        {
            "stage": "Prospective / Before Level I",
            "term": "Before you arrive",
            "headline": "Decide whether you want physics-first training or a clinical professional program.",
            "courses": ["Keep calculus, physics, chemistry, and biology doors open", "Compare Life Sci, Chem/Phys Sci, iSci, MRSc, Eng Phys"],
            "requirements": ["Understand that MedBioPhys is Physics & Astronomy; MRSc is separate McMaster-Mohawk clinical training."],
            "research": ["Browse faculty research areas early, but do not cold email everyone yet."],
            "actions": ["Read the MedBioPhys vs MRSc guide", "Plan a full first-year physics sequence if possible", "Start a simple Python habit if you are imaging/data curious"],
            "links": [("MedBioPhys vs MRSc", "medbiophys-vs-mrsc"), ("Honest guide", "medbiophys-explained")],
        },
        {
            "stage": "Level I",
            "term": "Fall",
            "headline": "Protect the Level II admission buckets before anything else.",
            "courses": ["One first-year physics course", "Calculus/math", "Chemistry", "Biology or biophysics if available"],
            "requirements": ["Start satisfying the math, intro physics, chemistry, and biology/CHEM/MATH admission groups."],
            "research": ["Attend department events and MUPS/physics community events; learn which professors supervise undergrads."],
            "actions": ["Build a tracker of completed requirements", "Go to office hours before you need rescue", "Keep one clean notebook or repo for code/math work"],
            "links": [("Level II admission guide", "level-ii-admission-guide")],
        },
        {
            "stage": "Level I",
            "term": "Winter",
            "headline": "Finish the admission puzzle and start thinking about summer research.",
            "courses": ["Second physics/modern physics option", "Second math/calculus option", "CHEM 1AA3 or required biology/linear algebra options"],
            "requirements": ["Check the 2025-2026 admission groups: GPA 5.0 minimum plus required first-year course groups."],
            "research": ["If you want summer research, start with 2-4 targeted emails in January/February, not a generic blast."],
            "actions": ["Run the Level II admission checker", "Prepare a one-page resume", "Ask one TA/professor what research in their area actually looks like"],
            "links": [("Requirement checklist", "level-ii-admission-guide"), ("Research guide", "research-guide")],
        },
        {
            "stage": "After Level I",
            "term": "Spring / Summer",
            "headline": "Use the summer to become easier to supervise.",
            "courses": ["No required course load assumed", "Optional: strengthen Python, linear algebra, or anatomy/biology gaps"],
            "requirements": ["Confirm Level II admission and any missing recommended courses."],
            "research": ["Possible routes: volunteer, paid RA, NSERC USRA if eligible and a supervisor supports you, or self-directed portfolio work."],
            "actions": ["Make a tiny project: image processing, simulation, literature map, or lab-data notebook", "Read 1-2 papers from a professor you may contact later"],
            "links": [("Cold email templates", "cold-email-templates"), ("NSERC and summer research", "nserc-usra-and-summer-research")],
        },
        {
            "stage": "Level II",
            "term": "Fall",
            "headline": "This is the shock year: physics/math/lab habits matter more than vibes.",
            "courses": ["PHYSICS 2C03", "PHYSICS 2P03", "DATASCI/PHYSICS 2G03", "MATH 2C03", "MATH 2X03/2MC3/2XA3", "BIOPHYS 2S03", "Anatomy/biochem options"],
            "requirements": ["Work through Level II core and any first-year note courses required by end of Level II."],
            "research": ["Choose a research direction shortlist: clinical imaging/radiation, health physics, molecular biophysics, soft matter, computation/data."],
            "actions": ["Start a faculty shortlist", "Save strong lab/code/course artifacts", "If co-op: understand application timing and resume expectations"],
            "links": [("Level II survival guide", "level-ii-survival-guide"), ("Co-op guide", "coop-guide")],
        },
        {
            "stage": "Level II",
            "term": "Winter",
            "headline": "This is the best time to line up summer research or NSERC USRA.",
            "courses": ["Finish Level II core", "Biochemistry option", "Lab/scientific computing/differential equations if not done"],
            "requirements": ["Use the program planner to make sure Level II and future Course List choices are coherent."],
            "research": ["For NSERC USRA: identify supervisor first, then complete Form 202 through the official system/internal department process."],
            "actions": ["Email targeted supervisors by January/February", "Ask about NSERC/SURA/paid RA possibilities", "Prepare transcript, resume, short research-fit paragraph"],
            "links": [("Program planner", "route:program_tool"), ("NSERC guide", "nserc-usra-and-summer-research")],
        },
        {
            "stage": "After Level II",
            "term": "Spring / Summer",
            "headline": "Turn research into evidence, not just a line on a resume.",
            "courses": ["USRA/RA/project work if secured", "Optional skill-building: Python, statistics, image processing, LaTeX"],
            "requirements": ["If doing co-op, keep the Science Careers sequence in mind."],
            "research": ["USRA or summer research should produce concrete outputs: poster, figures, code, methods summary, or a strong reference."],
            "actions": ["Track weekly accomplishments", "Ask what a good poster/report would look like", "Write a plain-English project summary before you forget details"],
            "links": [("Research guide", "research-guide"), ("Thesis guide", "thesis-and-senior-project-guide")],
        },
        {
            "stage": "Level III",
            "term": "Fall",
            "headline": "Choose your identity: medical physics, biological physics, soft matter, imaging/data, or health physics.",
            "courses": ["PHYSICS 2B03", "PHYSICS 3K03", "MATH 3C03", "BIOPHYS 3S03", "MEDPHYS 4B03", "Course List A/B/C electives"],
            "requirements": ["Start satisfying upper-year core plus the 12-unit Course List recommendation for your intended path."],
            "research": ["Talk to potential thesis supervisors before final year. Bring evidence: courses, code, lab skills, and a real reason for interest."],
            "actions": ["Run the program planner", "Pick a Course List track", "Ask upper years which courses actually support your goal"],
            "links": [("Upper-year planning", "upper-year-planning"), ("Course guides", "route:courses")],
        },
        {
            "stage": "Co-op path",
            "term": "Work terms",
            "headline": "Treat co-op as career evidence and research signal.",
            "courses": ["SCIENCE 3WT0 / 4WT0 / 5WT0 depending on sequence"],
            "requirements": ["Co-op changes timing; keep academic requirements mapped before and after work terms."],
            "research": ["Hospital research, imaging/data, health physics, nuclear, biotech, and academic labs can all feed thesis/grad/career choices."],
            "actions": ["Keep a project log", "Ask about posters/publications carefully", "Convert tasks into resume bullets and future interview stories"],
            "links": [("Co-op guide", "coop-guide"), ("Sample 5-year outline", "route:sample_course_outline_page")],
        },
        {
            "stage": "Level IV / Final academic year",
            "term": "Fall",
            "headline": "Thesis, Course List choices, and references now matter more than random electives.",
            "courses": ["BIOPHYS 4S03", "MEDPHYS 4RA3", "MEDPHYS/PHYSICS senior project", "Course List A/B/C electives"],
            "requirements": ["Check Level IV core and remaining upper-year focus-list units."],
            "research": ["Start thesis with a clear scope, meeting rhythm, data/code plan, and expected final deliverables."],
            "actions": ["Ask for reference letters early", "Draft grad/co-op/industry story around your project", "Keep a thesis one-pager updated"],
            "links": [("Thesis guide", "thesis-and-senior-project-guide"), ("Grad school/CAMPEP", "grad-school-campep-guide")],
        },
        {
            "stage": "Level IV / Graduating",
            "term": "Winter",
            "headline": "Finish with proof: thesis/report/poster, clear transcript story, and next-step applications.",
            "courses": ["MEDPHYS 4T03", "MEDPHYS 4U03 or imaging/health physics electives", "PHYSICS 3K03/3D03/remaining core where applicable"],
            "requirements": ["Confirm all graduation requirements with official advising and the calendar."],
            "research": ["Turn thesis/co-op/research into a portfolio: abstract, figures, code summary, poster, and recommendation letters."],
            "actions": ["For clinical medical physics: understand MSc/PhD, CAMPEP, residency, CCPM", "For industry: package Python/data/lab experience", "For health physics/nuclear: highlight radiation safety and instrumentation"],
            "links": [("Career pathways", "career-pathways"), ("Clinical medical physics", "clinical-medical-physics-roadmap")],
        },
    ]


def nserc_usra_guide():
    return {
        "headline": "NSERC USRA: the cleanest funded summer research route if you are eligible.",
        "official_facts": [
            "McMaster’s Research Office lists Summer 2026 USRAs as $6,000 plus supervisor/department top-up, normally 14-16 weeks full-time.",
            "Applications are completed through NSERC’s online system, but McMaster administers them internally through the eligible faculty/department.",
            "Students should apply through the department where the supervisor is appointed, which may not be the student’s home department.",
            "NSERC says applicants must have completed at least first-year/two academic terms before holding an award, meet citizenship/protected-person eligibility, and normally have at least a satisfactory cumulative average as defined by the institution.",
        ],
        "strong_application": [
            "Supervisor fit: the professor can immediately see why your coursework/skills match their research.",
            "Evidence of readiness: transcript is only one piece; include Python, labs, data analysis, microscopy, radiation, electronics, writing, or literature-review evidence.",
            "Specific project language: not 'I like medical physics'; say what method/problem you want to learn and why.",
            "Reliability signal: attach a clean resume, unofficial transcript if requested internally, and a concise availability window.",
            "Backup plan: apply to multiple suitable supervisors/departments where allowed, but never send a copy-paste email blast.",
        ],
    }


def research_faculty_contacts():
    return [
        {
            "name": "Kevin Diamond",
            "email": "diamonkr@mcmaster.ca",
            "area": "Clinical medical physics: radiation therapy and dosimetry",
            "fit": "Good fit if you are interested in treatment planning, dose measurement, QA, radiotherapy workflow, or the hospital-facing clinical physics path.",
            "student_work": "You might help with dosimetry analysis, treatment-plan data, image/dose QA, literature review, or clinical research support depending on active projects.",
            "source": "McMaster current faculty page lists radiation therapy/dosimetry and Juravinski Cancer Centre medical physicist role.",
        },
        {
            "name": "Chris Rowley",
            "email": "rowleycd@mcmaster.ca",
            "area": "MRI and medical physics",
            "fit": "Good fit if you like imaging physics, signal processing, Python/MATLAB, anatomy, and clinical imaging questions.",
            "student_work": "You might work on MRI data analysis, image quality, reconstruction/processing, literature review, or pipeline validation.",
            "source": "McMaster current faculty page lists MRI and medical physics.",
        },
        {
            "name": "Fiona McNeill",
            "email": "fmcneill@mcmaster.ca",
            "area": "Radiation-based biomedical devices and in vivo toxic element measurement",
            "fit": "Good fit for health physics, radiation instrumentation, XRF/NAA, detector methods, and human exposure/measurement projects.",
            "student_work": "You might support device/data analysis, calibration, radiation-method literature review, or health-physics instrumentation work.",
            "source": "McMaster Medical Physics faculty and RadGrad research pages describe radiation techniques for measuring toxic elements.",
        },
        {
            "name": "Cecile Fradin",
            "email": "fradin@mcmaster.ca",
            "area": "Experimental molecular biophysics",
            "fit": "Good fit if you like proteins, membranes, condensates, morphogen gradients, microscopy, optical tools, and quantifying living systems.",
            "student_work": "You might do image analysis, microscopy support, simulations/modeling, single-molecule dynamics, or literature/data work.",
            "source": "McMaster current faculty and molecular biophysics pages describe optical tools and biological dynamics.",
        },
        {
            "name": "Maikel Rheinstadter",
            "email": "rheinstadter@mcmaster.ca",
            "area": "Membrane and protein biophysics using X-ray/neutron scattering",
            "fit": "Good fit if you like membranes, proteins, soft matter, scattering, nanomedicine, drug-membrane interactions, or origin-of-life adjacent work.",
            "student_work": "You might analyze scattering data, model membrane structure/dynamics, prepare literature maps, or support experimental data workflows.",
            "source": "McMaster current faculty page lists membrane/protein structure and dynamics; seminar page describes membrane biophysics projects.",
        },
        {
            "name": "Paul Higgs",
            "email": "higgsp@mcmaster.ca",
            "area": "Computational/theoretical biophysics and origin of life",
            "fit": "Good fit if you like modeling, evolution, RNA world, protocells, viruses, simulations, and computational biology.",
            "student_work": "You might write simulations, analyze evolutionary models, read origin-of-life literature, or build computational experiments.",
            "source": "McMaster current faculty page lists origin of life, RNA world, protocells, RNA viruses, and computational biophysics.",
        },
        {
            "name": "Kari Dalnoki-Veress",
            "email": "dalnoki@mcmaster.ca",
            "area": "Soft and living matter at surfaces and interfaces",
            "fit": "Good fit if you like polymers, soft colloids, vesicles, microswimmers, imaging, force measurement, and living/soft matter experiments.",
            "student_work": "You might help with image analysis, microfluidic/soft matter experiments, surface/interface measurements, or data processing.",
            "source": "McMaster current faculty and soft matter/biophysics pages describe soft/living matter, microswimmers, vesicles, and interfaces.",
        },
        {
            "name": "An-Chang Shi",
            "email": "shi@mcmaster.ca",
            "area": "Soft condensed matter theory",
            "fit": "Good fit if you prefer theory/computation around polymers, liquid crystals, surfactants, colloids, biomaterials, and phase behavior.",
            "student_work": "You might support simulations, analytical modeling, reading theory papers, or coding phase-behavior calculations.",
            "source": "McMaster current faculty page describes soft condensed matter theory and polymer/colloid/biomaterial systems.",
        },
        {
            "name": "Michael Noseworthy",
            "email": "nosewor@mcmaster.ca",
            "area": "MRI, brain injury, musculoskeletal imaging, and cancer imaging",
            "fit": "Good fit if you want medical imaging research adjacent to hospitals, MRI methods, anatomy, and clinical datasets.",
            "student_work": "You might help with MRI data processing, segmentation, quality checks, imaging literature review, or analysis notebooks.",
            "source": "McMaster adjunct faculty page lists MRI, brain injury, musculoskeletal imaging, and cancer.",
        },
    ]


def research_outreach_template():
    return {
        "subject": "Undergraduate research inquiry - [specific method/topic]",
        "body": [
            "Dear Professor [Name],",
            "I am a Level [I/II/III/IV] Medical & Biological Physics student interested in [their specific area]. I read that your group works on [specific project/method from their page], and I am especially interested in [one concrete reason].",
            "My relevant background is [2-3 courses/skills: e.g., PHYSICS 2G03, Python, medical imaging, lab methods, radiation, biochemistry]. I am looking for [summer research / NSERC USRA / thesis supervision / volunteer research] and would be grateful to ask whether there may be a fit.",
            "I attached my resume and transcript. If you are not taking students, I would also appreciate advice on what skills or courses would make me a stronger applicant later.",
            "Best, [Name]",
        ],
        "rules": [
            "Email fewer people, better. Two tailored emails beat ten generic ones.",
            "Lead with fit, not desperation. Mention a method, paper, course connection, or project theme.",
            "Attach a one-page resume and transcript only when appropriate/requested.",
            "If no response after 7-10 days, send one polite follow-up, then move on.",
        ],
    }


def roadmap_sources():
    return [
        ("McMaster 2025-2026 Undergraduate Calendar", "https://academiccalendars.romcmaster.ca/preview_program.php?catoid=58&poid=29965&returnto=12628"),
        ("McMaster Physics current faculty", "https://physics.mcmaster.ca/people/current-faculty/"),
        ("Medical Physics faculty", "https://physics.mcmaster.ca/research/research-landing-pages/medical-physics/people-medical-physics/"),
        ("Soft Condensed Matter & Biophysics faculty", "https://physics.mcmaster.ca/research/research-landing-pages/soft-condensed-matter-and-biophysics/people-soft-condensed-matter-and-biophysics/"),
        ("RadGrad research", "https://radgrad.physics.mcmaster.ca/research/"),
        ("McMaster USRA Summer 2026", "https://research.mcmaster.ca/funding/undergraduate-student-research-award-usra/"),
        ("NSERC USRA program", "https://nserc-crsng.canada.ca/en/funding-opportunity/undergraduate-student-research-awards"),
    ]


def program_planner_groups(grouped_rules):
    course_codes = sorted(
        {
            normalize_course_code(code)
            for rules in grouped_rules.values()
            for rule in rules
            for group in normalize_option_groups(rule.course_options)
            for code in group
        }
    )
    courses = {course.code: course for course in Course.query.filter(Course.code.in_(course_codes)).all()}
    planner_groups = []
    for group_key, rules in grouped_rules.items():
        group_rules = []
        for rule in rules:
            options = []
            for option_group in normalize_option_groups(rule.course_options):
                for code in option_group:
                    course = courses.get(code)
                    options.append(
                        {
                            "code": code,
                            "title": course.title if course else "Check calendar listing",
                            "units": course.units if course else rule.option_units,
                            "category": course.category if course else "Calendar",
                            "level": course.level if course else "",
                            "tracks": course.track_tags if course else [],
                        }
                    )
            group_rules.append({"rule": rule, "options": options})
        planner_groups.append({"key": group_key, "label": labelize(group_key), "rules": group_rules})
    return planner_groups


def sample_course_outline():
    terms = [
        {
            "year": "Year 1",
            "term": "2021 Fall",
            "program": "Chemical & Physical Sciences Gateway",
            "note": "Gateway foundation: biology, chemistry, calculus, and first physics.",
            "courses": [
                ("BIOLOGY 1A03", "Cellular and Molecular Biology", "3 units"),
                ("BIOPHYS 1S03", "Biophysics: Movements and Senses", "3 units"),
                ("CHEM 1A03", "Introductory Chemistry I", "3 units"),
                ("MATH 1A03", "Calculus For Science I", "3 units"),
                ("PHYSICS 1C03", "Physics for Chemical and Physical Sciences", "3 units"),
                ("BIOSAFE 1BS0", "Biosafety Training", "0 units"),
                ("WHMIS 1A00", "Intro to Health and Safety", "0 units"),
            ],
        },
        {
            "year": "Year 1",
            "term": "2022 Winter",
            "program": "Chemical & Physical Sciences Gateway",
            "note": "Second gateway term: chemistry II, medical imaging exposure, calculus II, linear algebra, and modern physics.",
            "courses": [
                ("CHEM 1AA3", "Introductory Chemistry II", "3 units"),
                ("LIFESCI 1D03", "Medical Imaging Physics", "3 units"),
                ("MATH 1AA3", "Calculus For Science II", "3 units"),
                ("MATH 1B03", "Linear Algebra I", "3 units"),
                ("PHYSICS 1CC3", "Modern Physics for Chemical and Physical Sciences", "3 units"),
            ],
        },
        {
            "year": "Year 2",
            "term": "2022 Fall",
            "program": "Medical & Biological Physics",
            "note": "First MedBioPhys term with computing, anatomy/physiology, advanced calculus, E&M, and modern physics.",
            "courses": [
                ("DATASCI 2G03", "Scientific Computing", "3 units"),
                ("KINESIOL 2Y03", "Human Anatomy and Physiology I", "3 units"),
                ("MATH 2X03", "Advanced Calculus I", "3 units"),
                ("PHYSICS 2B03", "Electricity and Magnetism I", "3 units"),
                ("PHYSICS 2C03", "Modern Physics", "3 units"),
            ],
        },
        {
            "year": "Year 2",
            "term": "2023 Winter",
            "program": "Medical & Biological Physics",
            "note": "Core MedBioPhys term with biochemistry, biophysics, machine learning, differential equations, and lab.",
            "courses": [
                ("BIOCHEM 2EE3", "Metabolism and Physiological Chemistry", "3 units"),
                ("BIOPHYS 2S03", "Explorations in Medical and Biological Physics", "3 units"),
                ("DATASCI 3ML3", "Neural Networks and Machine Learning", "3 units"),
                ("MATH 2C03", "Introduction to Differential Equations", "3 units"),
                ("PHYSICS 2P03", "Introductory Laboratory", "3 units"),
                ("SCIENCE 2C00", "Skills for Career Success: Science", "0 units"),
            ],
        },
        {
            "year": "Year 3",
            "term": "2023 Fall",
            "program": "Medical & Biological Physics Co-op",
            "note": "Upper-year physics/biophysics foundation before the first 8-month co-op block.",
            "courses": [
                ("BIOCHEM 3G03", "Proteins and Nucleic Acids", "3 units"),
                ("BIOPHYS 3S03", "Soft Condensed Matter Physics", "3 units"),
                ("MATH 3C03", "Mathematical Physics I", "3 units"),
                ("MEDPHYS 4B03", "Radioactivity and Radiation in Medical Physics", "3 units"),
                ("PHYSICS 3MM3", "Quantum Mechanics I", "3 units"),
                ("SCIENCE 3C00", "Advanced Job Search Skills: Science Co-op", "0 units"),
            ],
        },
        {
            "year": "Year 3",
            "term": "2024 Winter",
            "program": "Co-op work term",
            "note": "Science co-op work term at University of Alabama at Birmingham.",
            "courses": [("SCIENCE 3WT0", "Science Co-op Work Term", "0 units")],
        },
        {
            "year": "Year 3",
            "term": "2024 Spring/Summer",
            "program": "Co-op work term",
            "note": "Continuation of Science co-op work term at University of Alabama at Birmingham.",
            "courses": [("SCIENCE 3WT0", "Science Co-op Work Term", "0 units")],
        },
        {
            "year": "Year 4",
            "term": "2024 Fall",
            "program": "Medical & Biological Physics Co-op",
            "note": "Return from co-op into molecular biophysics, health physics, radiation lab methods, computing, and senior project start.",
            "courses": [
                ("BIOPHYS 4S03", "Introduction to Molecular Biophysics", "3 units"),
                ("MATH 1MP3", "Introduction to Mathematical Scientific Computation", "3 units"),
                ("MEDPHYS 4F03", "Fundamentals of Health Physics", "3 units"),
                ("MEDPHYS 4RA3", "Radiation and Radioisotope Methodology I", "3 units"),
                ("MEDPHYS 4Y06A", "Senior Research Project", "multi-term"),
            ],
        },
        {
            "year": "Year 4",
            "term": "2025 Winter",
            "program": "Medical & Biological Physics Co-op",
            "note": "Clinical and radiation-focused capstone term plus thermodynamics/stat mech and inquiry physics.",
            "courses": [
                ("MEDPHYS 4T03", "Physics in Medicine", "3 units"),
                ("MEDPHYS 4U03", "Radiation Biology", "3 units"),
                ("MEDPHYS 4Y06B", "Senior Research Project", "6 units"),
                ("PHYSICS 3D03", "Inquiry in Physics", "3 units"),
                ("PHYSICS 3K03", "Thermodynamics and Statistical Mechanics", "3 units"),
            ],
        },
        {
            "year": "Year 4",
            "term": "2025 Spring/Summer",
            "program": "Co-op work term",
            "note": "Science co-op work term at University of Alabama at Birmingham.",
            "courses": [("SCIENCE 4WT0", "Science Co-op Work Term", "0 units")],
        },
        {
            "year": "Year 5",
            "term": "2025 Fall",
            "program": "Co-op work term",
            "note": "Continuation/final co-op work term at University of Alabama at Birmingham.",
            "courses": [("SCIENCE 5WT0", "Science Co-op Work Term", "0 units")],
        },
    ]
    codes = [normalize_course_code(code) for term in terms for code, _, _ in term["courses"]]
    thesis = {
        "title": "Honours thesis / senior research project",
        "courses": ["MEDPHYS 4Y06A", "MEDPHYS 4Y06B"],
        "placement": "Started in 2024 Fall and completed in 2025 Winter alongside upper-year Medical Physics and Physics courses.",
        "why_it_matters": "This is where the degree can turn from course-taking into evidence of research independence: literature review, data/methods, supervisor meetings, analysis, poster/oral communication, and a final report.",
        "student_actions": [
            "Start supervisor conversations before final year, especially if you want medical imaging, radiation, health physics, computation, or wet-lab biophysics.",
            "Treat the project like a portfolio artifact: keep clean figures, reproducible code or lab notes, and a plain-English project summary.",
            "Use the project to test whether you actually like graduate-school-style work before applying to MSc, PhD, CAMPEP, or research-heavy industry paths.",
        ],
    }
    coop = {
        "title": "Co-op sequence",
        "courses": ["SCIENCE 3WT0", "SCIENCE 4WT0", "SCIENCE 5WT0"],
        "placement": "This sample shows an 8-month work term in 2024 Winter/Spring-Summer and a later 2025 Spring-Summer/Fall work-term block.",
        "why_it_matters": "Co-op changes the pacing of the degree. The tradeoff is a longer timeline; the upside is paid experience, stronger references, project stories, and a clearer sense of whether you prefer hospital research, imaging/data, health physics, nuclear, biotech, or academic research.",
        "student_actions": [
            "Before applying: build a one-page resume that translates physics labs, Python, data analysis, anatomy/biochemistry, and radiation/imaging coursework into employer language.",
            "During the work term: track projects, tools, datasets, posters, abstracts, reports, and supervisor feedback while details are fresh.",
            "After the work term: convert the experience into resume bullets, research questions, grad-school statements, and mentor/course-review contributions for younger students.",
        ],
    }
    return {
        "title": "Sample course outline: five-year MedBioPhys co-op path",
        "source_note": "Built from the provided transcript with grades removed. This is one student's actual sequence, not an official recommended schedule.",
        "terms": terms,
        "thesis": thesis,
        "coop": coop,
        "codes": codes,
    }


def get_moderated_target(target_type, target_id):
    models = {"CourseReview": CourseReview, "MentorProfile": MentorProfile, "QuestionSubmission": QuestionSubmission}
    model = models.get(target_type)
    if not model:
        abort(404)
    target = db.session.get(model, target_id)
    if not target:
        abort(404)
    return target


def notify_user(user_id, title, body, category, link_url="", actor_label="Isocentre", target_type="", target_id=None):
    if not user_id:
        return None
    notification = Notification(
        user_id=user_id,
        title=clean_text(title),
        body=clean_text(body),
        category=clean_text(category) or "general",
        link_url=link_url or "",
        actor_label=clean_text(actor_label) or "Isocentre",
        target_type=target_type or "",
        target_id=target_id,
    )
    db.session.add(notification)
    return notification


def notify_moderation_result(target, target_type, action):
    user_id = getattr(target, "user_id", None)
    if not user_id or action not in {"approve", "reject", "hide"}:
        return
    label = {
        "CourseReview": "course review",
        "MentorProfile": "mentor profile",
        "QuestionSubmission": "question",
    }.get(target_type, "submission")
    action_label = {"approve": "approved", "reject": "rejected", "hide": "hidden"}[action]
    title = f"Your {label} was {action_label}"
    if action == "approve":
        body = f"Your {label} is now live or accepted in Isocentre."
    elif action == "reject":
        body = f"Your {label} was not published. Check the guidelines and submit again if useful."
    else:
        body = f"Your {label} is no longer public."
    link_url = url_for("main.notifications")
    if target_type == "CourseReview" and getattr(target, "course", None):
        link_url = url_for("main.course_reviews", code=target.course.code)
    elif target_type == "MentorProfile":
        link_url = url_for("main.mentors")
    elif target_type == "QuestionSubmission":
        link_url = url_for("main.community")
    notify_user(user_id, title, body, "moderation", link_url, target_type=target_type, target_id=target.id)


def notify_course_review_followers(review):
    course = review.course
    if not course:
        return
    saved_items = UserCourseStatus.query.filter_by(course_id=course.id).all()
    for item in saved_items:
        if item.user_id == review.user_id:
            continue
        notify_user(
            item.user_id,
            f"New review for {course.code}",
            "A new approved student review is available for a course in your planner.",
            "course-review",
            url_for("main.course_reviews", code=course.code),
            target_type="CourseReview",
            target_id=review.id,
        )


def notify_higher_years(question, asker):
    recipients = higher_year_users(asker)
    for recipient in recipients:
        profile_bits = [asker.stage]
        if asker.goal:
            profile_bits.append(asker.goal)
        if asker.pathway_tags:
            profile_bits.append(", ".join(asker.pathway_tags))
        notify_user(
            recipient.id,
            "New upper-year question",
            f"{asker.display_name} ({'; '.join(profile_bits)}) asked about {question.topic}.",
            "upper-year-question",
            url_for("main.question_detail", question_id=question.id),
            actor_label=asker.display_name,
            target_type="QuestionSubmission",
            target_id=question.id,
        )
    return len(recipients)


class ListPagination:
    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = max(1, (total + per_page - 1) // per_page) if total else 0
        self.has_prev = page > 1
        self.has_next = self.pages > page
        self.prev_num = page - 1
        self.next_num = page + 1


def paginate_list(items, page, per_page):
    total = len(items)
    pages = max(1, (total + per_page - 1) // per_page) if total else 1
    page = min(page, pages)
    start = (page - 1) * per_page
    return ListPagination(items[start : start + per_page], page, per_page, total)


def filter_mentors(mentors, query="", tag="", availability="available", contact="any"):
    query = clean_text(query).lower()
    tag = clean_text(tag).lower()
    filtered = []
    for mentor in mentors:
        tags = [str(item).lower() for item in (mentor.pathway_tags or []) + (mentor.experience_tags or [])]
        haystack = " ".join(
            [
                mentor.display_name or "",
                mentor.role_year or "",
                mentor.bio or "",
                mentor.contact_preference or "",
                mentor.public_contact_text or "",
                " ".join(tags),
            ]
        ).lower()
        if query and query not in haystack:
            continue
        if tag and tag not in tags and tag not in haystack:
            continue
        if availability == "available" and not mentor.mentorship_available:
            continue
        if availability == "unavailable" and mentor.mentorship_available:
            continue
        if contact == "dm" and not mentor.user_id:
            continue
        if contact == "public" and mentor.user_id:
            continue
        filtered.append(mentor)
    return filtered


def mentor_matches_for_user(user, limit=6):
    if not user:
        return []
    mentors = (
        MentorProfile.query.filter_by(status=ModerationStatus.APPROVED)
        .filter(or_(MentorProfile.user_id.is_(None), MentorProfile.user_id != user.id))
        .order_by(MentorProfile.featured.desc(), MentorProfile.mentorship_available.desc(), MentorProfile.updated_at.desc())
        .all()
    )
    interests = {str(item).lower() for item in user.pathway_tags or []}
    scored = []
    for mentor in mentors:
        tags = {str(item).lower() for item in (mentor.pathway_tags or []) + (mentor.experience_tags or [])}
        score = len(interests & tags)
        if mentor.mentorship_available:
            score += 2
        if mentor.user_id:
            score += 1
        if mentor.featured:
            score += 1
        scored.append((score, mentor))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [mentor for _, mentor in scored[:limit]]


def mentor_tag_cloud(mentors):
    counts = defaultdict(int)
    for mentor in mentors:
        for tag in (mentor.pathway_tags or []) + (mentor.experience_tags or []):
            cleaned = clean_text(tag)
            if cleaned:
                counts[cleaned] += 1
    return [tag for tag, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:16]]


def question_starter_topics(user):
    base = [
        "Choosing Level II courses",
        "Finding research or NSERC USRA",
        "Preparing for PHYSICS 2B03 / 2C03",
        "Co-op applications",
        "Clinical medical physics path",
        "Grad school and CAMPEP",
    ]
    if user and user.pathway_tags:
        return [f"{tag} pathway advice" for tag in user.pathway_tags[:3]] + base
    return base


def higher_year_users(asker):
    asker_rank = stage_rank(asker.stage)
    if asker_rank < 0:
        return []
    users = (
        UserAccount.query.filter(UserAccount.id != asker.id)
        .order_by(UserAccount.stage, UserAccount.display_name)
        .all()
    )
    return [user for user in users if stage_rank(user.stage) > asker_rank]


def can_view_question(user, question):
    if is_admin() or user.id == question.user_id:
        return True
    return stage_rank(user.stage) > stage_rank(question.stage)


def stage_rank(stage):
    ranks = {
        "Prospective": 0,
        "Level I": 1,
        "Level II": 2,
        "Upper-year": 3,
        "Graduating": 4,
        "Alumni": 5,
    }
    return ranks.get(clean_text(stage), -1)


def mentor_owner_options():
    return UserAccount.query.order_by(UserAccount.display_name, UserAccount.email).limit(200).all()


def save_admin_mentor_form(mentor):
    owner_email = normalize_email(request.form.get("owner_email", ""))
    private_email = normalize_email(request.form.get("private_email", ""))
    owner = UserAccount.query.filter_by(email=owner_email).first() if owner_email else None
    effective_email = owner.email if owner else private_email
    if not effective_email:
        flash("Add a private email or attach the profile to an existing user account.", "error")
        return False
    if owner_email and not owner:
        flash("No user account exists for that owner email. Leave owner blank or create the account first.", "error")
        return False

    mentor.user_id = owner.id if owner else None
    mentor.display_name = clean_text(request.form.get("display_name"))[:120]
    mentor.role_year = clean_text(request.form.get("role_year"))[:120]
    mentor.pathway_tags = split_tags(request.form.get("pathway_tags", ""))
    mentor.experience_tags = split_tags(request.form.get("experience_tags", ""))
    mentor.bio = clean_text(request.form.get("bio"))
    mentor.contact_preference = clean_text(request.form.get("contact_preference"))[:120] or "Isocentre inbox"
    mentor.public_contact_text = clean_text(request.form.get("public_contact_text"))[:240]
    mentor.private_email = effective_email
    mentor.email_hash = email_hash(effective_email)
    mentor.status = clean_text(request.form.get("status")) or ModerationStatus.APPROVED
    if mentor.status not in {
        ModerationStatus.AWAITING_VERIFICATION,
        ModerationStatus.PENDING,
        ModerationStatus.APPROVED,
        ModerationStatus.REJECTED,
        ModerationStatus.HIDDEN,
    }:
        mentor.status = ModerationStatus.APPROVED
    mentor.mentorship_available = request.form.get("mentorship_available", "yes") == "yes"
    mentor.featured = request.form.get("featured", "no") == "yes"

    if not mentor.display_name or not mentor.role_year or not mentor.bio:
        flash("Display name, role/year, and bio are required.", "error")
        return False
    if mentor.status in {ModerationStatus.PENDING, ModerationStatus.APPROVED} and not mentor.verified_at:
        mentor.verified_at = datetime.now(timezone.utc)
    mentor.moderated_at = datetime.now(timezone.utc)
    return True


def delete_mentor_message(message):
    Notification.query.filter_by(target_type="MentorMessage", target_id=message.id).delete(synchronize_session=False)
    db.session.add(AdminAuditLog(action="delete", target_type="MentorMessage", target_id=message.id, detail=message.subject))
    db.session.delete(message)


def delete_user_account(user):
    mentor_ids = [row.id for row in MentorProfile.query.with_entities(MentorProfile.id).filter_by(user_id=user.id).all()]
    message_query = MentorMessage.query.filter(or_(MentorMessage.sender_id == user.id, MentorMessage.recipient_id == user.id))
    if mentor_ids:
        message_query = message_query.union(MentorMessage.query.filter(MentorMessage.mentor_id.in_(mentor_ids)))
    message_ids = [message.id for message in message_query.all()]
    if message_ids:
        Notification.query.filter(Notification.target_type == "MentorMessage", Notification.target_id.in_(message_ids)).delete(
            synchronize_session=False
        )
        MentorMessage.query.filter(MentorMessage.id.in_(message_ids)).delete(synchronize_session=False)

    if mentor_ids:
        Notification.query.filter(Notification.target_type == "MentorProfile", Notification.target_id.in_(mentor_ids)).delete(synchronize_session=False)
        MentorProfile.query.filter(MentorProfile.id.in_(mentor_ids)).delete(synchronize_session=False)

    review_ids = [row.id for row in CourseReview.query.with_entities(CourseReview.id).filter_by(user_id=user.id).all()]
    if review_ids:
        Notification.query.filter(Notification.target_type == "CourseReview", Notification.target_id.in_(review_ids)).delete(synchronize_session=False)
        CourseReview.query.filter(CourseReview.id.in_(review_ids)).delete(synchronize_session=False)

    question_ids = [row.id for row in QuestionSubmission.query.with_entities(QuestionSubmission.id).filter_by(user_id=user.id).all()]
    if question_ids:
        Notification.query.filter(Notification.target_type == "QuestionSubmission", Notification.target_id.in_(question_ids)).delete(
            synchronize_session=False
        )
        QuestionSubmission.query.filter(QuestionSubmission.id.in_(question_ids)).delete(synchronize_session=False)

    UserCourseStatus.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    UserSavedGuide.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    Notification.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    db.session.add(AdminAuditLog(action="delete", target_type="UserAccount", target_id=user.id, detail=user.email))
    db.session.delete(user)


def require_admin():
    if not is_admin():
        abort(403)


def is_admin():
    return bool(session.get("admin"))


def group_resources(links):
    grouped = defaultdict(list)
    for link in links:
        grouped[link.category].append(link)
    return grouped


def normalize_course_code(value):
    return "".join(str(value).upper().replace("-", " ").split())


def clean_text(value):
    if value is None:
        return ""
    return " ".join(str(value).strip().split()) or ""


def split_tags(value):
    return [clean_text(tag) for tag in str(value).split(",") if clean_text(tag)]


def labelize(value):
    label = str(value).replace("-", " ").title()
    return label.replace(" Iii", " III").replace(" Ii", " II").replace(" Iv", " IV")


def bounded_int(value, low, high, default):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def success_message(sent):
    if sent:
        return "Check your McMaster email for a verification link. After verification, the submission goes to moderation."
    return "Submission saved, but SMTP is not configured. An admin can still inspect it; configure mail env vars to send verification links."
