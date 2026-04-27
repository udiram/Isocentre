from datetime import datetime, timezone

from sqlalchemy import JSON

from . import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Page(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    section = db.Column(db.String(80), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    body_markdown = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text, nullable=False, default="")
    source_links = db.Column(JSON, nullable=False, default=list)
    source_confidence = db.Column(db.String(40), nullable=False, default="official-and-unofficial")
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    last_verified_at = db.Column(db.DateTime, nullable=True)


class Course(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40), unique=True, nullable=False, index=True)
    title = db.Column(db.String(160), nullable=False)
    official_title = db.Column(db.String(180), nullable=False, default="")
    category = db.Column(db.String(80), nullable=False)
    level = db.Column(db.Integer, nullable=False, default=0)
    units = db.Column(db.Integer, nullable=False, default=3)
    calendar_url = db.Column(db.String(500), nullable=True)
    source_urls = db.Column(JSON, nullable=False, default=list)
    aliases = db.Column(JSON, nullable=False, default=list)
    requirement_roles = db.Column(JSON, nullable=False, default=list)
    track_tags = db.Column(JSON, nullable=False, default=list)
    official_notes = db.Column(db.Text, nullable=False, default="")
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    workload = db.Column(db.Integer, nullable=False)
    math_intensity = db.Column(db.Integer, nullable=False)
    coding_intensity = db.Column(db.Integer, nullable=False)
    memorization_intensity = db.Column(db.Integer, nullable=False)
    before_starting = db.Column(db.Text, nullable=False)
    resources = db.Column(db.Text, nullable=False)
    failure_points = db.Column(db.Text, nullable=False)
    study_strategy = db.Column(db.Text, nullable=False)
    unlocks = db.Column(db.Text, nullable=False)
    pair_with = db.Column(db.Text, nullable=False)
    student_tips = db.Column(db.Text, nullable=False)
    student_reported = db.Column(db.Text, nullable=False, default="")
    last_verified_at = db.Column(db.DateTime, nullable=True)

    reviews = db.relationship("CourseReview", back_populates="course", lazy="dynamic")


class UserAccount(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(120), nullable=False)
    stage = db.Column(db.String(80), nullable=False, default="Level I")
    pathway_tags = db.Column(JSON, nullable=False, default=list)
    goal = db.Column(db.String(180), nullable=False, default="")
    is_mcmaster = db.Column(db.Boolean, nullable=False, default=False, index=True)
    last_login_at = db.Column(db.DateTime, nullable=True)

    saved_courses = db.relationship("UserCourseStatus", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    saved_guides = db.relationship("UserSavedGuide", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")


class UserCourseStatus(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_account.id"), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False, index=True)
    status = db.Column(db.String(40), nullable=False, default="planned", index=True)
    term_label = db.Column(db.String(80), nullable=False, default="")
    note = db.Column(db.Text, nullable=False, default="")

    user = db.relationship("UserAccount", back_populates="saved_courses")
    course = db.relationship("Course")
    __table_args__ = (db.UniqueConstraint("user_id", "course_id", name="uq_user_course_status"),)


class UserSavedGuide(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_account.id"), nullable=False, index=True)
    page_id = db.Column(db.Integer, db.ForeignKey("page.id"), nullable=False, index=True)

    user = db.relationship("UserAccount", back_populates="saved_guides")
    page = db.relationship("Page")
    __table_args__ = (db.UniqueConstraint("user_id", "page_id", name="uq_user_saved_guide"),)


class RequirementRule(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False, index=True)
    requirement_set = db.Column(db.String(80), nullable=False, default="level-ii-admission", index=True)
    label = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    course_options = db.Column(JSON, nullable=False, default=list)
    rule_type = db.Column(db.String(40), nullable=False, default="any")
    required_count = db.Column(db.Integer, nullable=False, default=1)
    units_required = db.Column(db.Integer, nullable=False, default=0)
    option_units = db.Column(db.Integer, nullable=False, default=3)
    track = db.Column(db.String(80), nullable=False, default="")
    advisory_note = db.Column(db.Text, nullable=False, default="")
    sort_order = db.Column(db.Integer, nullable=False, default=0)


class ResourceLink(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_official = db.Column(db.Boolean, default=True, nullable=False)


class ModerationStatus:
    AWAITING_VERIFICATION = "awaiting_verification"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    HIDDEN = "hidden"


class CourseReview(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False, index=True)
    course = db.relationship("Course", back_populates="reviews")
    user_id = db.Column(db.Integer, db.ForeignKey("user_account.id"), nullable=True, index=True)
    user = db.relationship("UserAccount")
    submitter_email_hash = db.Column(db.String(128), nullable=False, index=True)
    email_private = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(40), nullable=False, default=ModerationStatus.AWAITING_VERIFICATION, index=True)
    term_taken = db.Column(db.String(80), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    workload = db.Column(db.Integer, nullable=False)
    usefulness = db.Column(db.Integer, nullable=False)
    math_intensity = db.Column(db.Integer, nullable=False)
    coding_intensity = db.Column(db.Integer, nullable=False)
    memorization_intensity = db.Column(db.Integer, nullable=False)
    would_take_again = db.Column(db.Boolean, nullable=False, default=True)
    advice = db.Column(db.Text, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    moderated_at = db.Column(db.DateTime, nullable=True)


class MentorProfile(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_account.id"), nullable=True, index=True)
    user = db.relationship("UserAccount")
    display_name = db.Column(db.String(120), nullable=False)
    role_year = db.Column(db.String(120), nullable=False)
    pathway_tags = db.Column(JSON, nullable=False, default=list)
    experience_tags = db.Column(JSON, nullable=False, default=list)
    bio = db.Column(db.Text, nullable=False)
    contact_preference = db.Column(db.String(120), nullable=False)
    public_contact_text = db.Column(db.String(240), nullable=False, default="")
    private_email = db.Column(db.String(255), nullable=False)
    email_hash = db.Column(db.String(128), nullable=False, index=True)
    status = db.Column(db.String(40), nullable=False, default=ModerationStatus.AWAITING_VERIFICATION, index=True)
    mentorship_available = db.Column(db.Boolean, nullable=False, default=True)
    featured = db.Column(db.Boolean, nullable=False, default=False, index=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    moderated_at = db.Column(db.DateTime, nullable=True)


class QuestionSubmission(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_account.id"), nullable=True, index=True)
    user = db.relationship("UserAccount")
    stage = db.Column(db.String(80), nullable=False)
    topic = db.Column(db.String(160), nullable=False)
    body = db.Column(db.Text, nullable=False)
    private_email = db.Column(db.String(255), nullable=False)
    email_hash = db.Column(db.String(128), nullable=False, index=True)
    status = db.Column(db.String(40), nullable=False, default=ModerationStatus.AWAITING_VERIFICATION, index=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    moderated_at = db.Column(db.DateTime, nullable=True)


class EmailVerificationToken(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    purpose = db.Column(db.String(80), nullable=False)
    target_type = db.Column(db.String(80), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    token_hash = db.Column(db.String(128), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    consumed_at = db.Column(db.DateTime, nullable=True)


class AdminAuditLog(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(80), nullable=False)
    target_type = db.Column(db.String(80), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    detail = db.Column(db.Text, nullable=False, default="")


class Notification(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_account.id"), nullable=False, index=True)
    user = db.relationship("UserAccount")
    title = db.Column(db.String(180), nullable=False)
    body = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False, default="general", index=True)
    link_url = db.Column(db.String(500), nullable=False, default="")
    actor_label = db.Column(db.String(120), nullable=False, default="Isocentre")
    target_type = db.Column(db.String(80), nullable=False, default="", index=True)
    target_id = db.Column(db.Integer, nullable=True, index=True)
    read_at = db.Column(db.DateTime, nullable=True, index=True)


class MentorMessage(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey("mentor_profile.id"), nullable=False, index=True)
    mentor = db.relationship("MentorProfile")
    sender_id = db.Column(db.Integer, db.ForeignKey("user_account.id"), nullable=False, index=True)
    sender = db.relationship("UserAccount", foreign_keys=[sender_id])
    recipient_id = db.Column(db.Integer, db.ForeignKey("user_account.id"), nullable=False, index=True)
    recipient = db.relationship("UserAccount", foreign_keys=[recipient_id])
    subject = db.Column(db.String(180), nullable=False)
    body = db.Column(db.Text, nullable=False)
    read_at = db.Column(db.DateTime, nullable=True, index=True)
    attachments = db.relationship("MentorMessageAttachment", back_populates="message", cascade="all, delete-orphan", lazy="dynamic")


class MentorMessageAttachment(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey("mentor_message.id"), nullable=False, index=True)
    message = db.relationship("MentorMessage", back_populates="attachments")
    original_filename = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(120), nullable=False, default="application/octet-stream")
    file_size = db.Column(db.Integer, nullable=False, default=0)
    data = db.Column(db.LargeBinary, nullable=False)
