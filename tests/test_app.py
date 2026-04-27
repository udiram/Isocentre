import pytest

from app import create_app, db
from app.models import (
    Course,
    CourseReview,
    MentorMessage,
    MentorProfile,
    ModerationStatus,
    Notification,
    QuestionSubmission,
    UserAccount,
    UserCourseStatus,
    UserSavedGuide,
)
from app.seed import seed_database


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
            "MAIL_SERVER": "",
        }
    )
    with app.app_context():
        db.create_all()
        seed_database(db.session)
        db.session.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_mvp_routes_return_success(client):
    routes = [
        "/",
        "/guide/medbiophys-explained",
        "/guide/medbiophys-vs-mrsc",
        "/guide/level-ii-admission-guide",
        "/guide/level-ii-survival-guide",
        "/courses",
        "/guide/research-guide",
        "/guide/coop-guide",
        "/guide/grad-school-campep-guide",
        "/guide/career-pathways",
        "/guide/clinical-medical-physics-roadmap",
        "/guide/health-physics-radiation-protection",
        "/guide/medical-imaging-ai-portfolio",
        "/guide/nserc-usra-and-summer-research",
        "/guide/thesis-and-senior-project-guide",
        "/tools/gpa",
        "/tools/requirements",
        "/tools/program",
        "/tools/cold-email",
        "/guide-map",
        "/roadmap",
        "/sample-course-outline",
        "/search",
        "/auth/login",
        "/auth/register",
        "/community",
        "/community/mentors",
        "/community/ask",
        "/notifications",
        "/messages",
        "/admin",
        "/resources",
    ]

    for route in routes:
        response = client.get(route)
        if route in {"/notifications", "/messages", "/community/ask"}:
            assert response.status_code == 302, route
        else:
            assert response.status_code == 200, route


def test_roadmap_has_research_and_outreach_structure(client):
    response = client.get("/roadmap")

    assert response.status_code == 200
    assert b"Semester by semester" in response.data
    assert b"NSERC USRA" in response.data
    assert b"Kevin Diamond" in response.data
    assert b"Undergraduate research inquiry" in response.data


def test_register_dashboard_and_saved_items(client, app):
    register = client.post(
        "/auth/register",
        data={
            "email": "planner@mcmaster.ca",
            "password": "strong-pass",
            "display_name": "Planner",
            "stage": "Level II",
            "pathway_tags": "clinical medical physics, imaging AI",
            "goal": "survive Level II",
        },
        follow_redirects=False,
    )
    assert register.status_code == 302

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert b"Level II dashboard" in dashboard.data

    save_course = client.post("/courses/PHYSICS2G03/save", data={"status": "completed"})
    assert save_course.status_code == 302
    save_guide = client.post("/guide/level-ii-survival-guide/save")
    assert save_guide.status_code == 302

    with app.app_context():
        user = UserAccount.query.filter_by(email="planner@mcmaster.ca").one()
        assert user.is_mcmaster is True
        assert UserCourseStatus.query.filter_by(user_id=user.id).count() == 1
        assert UserSavedGuide.query.filter_by(user_id=user.id).count() == 1


def test_register_requires_mcmaster_email(client, app):
    response = client.post(
        "/auth/register",
        data={
            "email": "student@example.com",
            "password": "strong-pass",
            "display_name": "External",
            "stage": "Level I",
        },
    )

    assert response.status_code == 400
    assert b"@mcmaster.ca" in response.data
    with app.app_context():
        assert UserAccount.query.filter_by(email="student@example.com").first() is None


def test_login_required_redirects_to_auth(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_resend_env_shortcut_configures_smtp(monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", "test-resend-key")
    monkeypatch.setenv("RESEND_FROM_EMAIL", "Isocentre <verify@example.com>")
    monkeypatch.delenv("MAIL_SERVER", raising=False)
    monkeypatch.delenv("MAIL_USERNAME", raising=False)
    monkeypatch.delenv("MAIL_PASSWORD", raising=False)
    monkeypatch.delenv("MAIL_DEFAULT_SENDER", raising=False)
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})

    assert app.config["MAIL_SERVER"] == "smtp.resend.com"
    assert app.config["MAIL_PORT"] == 587
    assert app.config["MAIL_USERNAME"] == "resend"
    assert app.config["MAIL_PASSWORD"] == "test-resend-key"
    assert app.config["MAIL_DEFAULT_SENDER"] == "Isocentre <verify@example.com>"


def test_verification_email_failure_is_graceful(app, monkeypatch):
    from app.email_utils import send_verification_email

    app.config.update(
        MAIL_SERVER="smtp.invalid.local",
        MAIL_PORT=587,
        MAIL_USERNAME="resend",
        MAIL_PASSWORD="bad-key",
        MAIL_DEFAULT_SENDER="Isocentre <verify@example.com>",
    )

    class BrokenSMTP:
        def __init__(self, *args, **kwargs):
            raise OSError("network unavailable")

    monkeypatch.setattr("app.email_utils.smtplib.SMTP", BrokenSMTP)
    with app.test_request_context("/"):
        assert send_verification_email("student@mcmaster.ca", "token") is False


def test_search_finds_courses_and_guides(client):
    response = client.get("/search?q=CAMPEP")
    assert response.status_code == 200
    assert b"CAMPEP" in response.data


def test_requirement_checker_statuses(client):
    response = client.post(
        "/api/requirements/check",
        json={"courses": ["PHYSICS 1A03", "PHYSICS 1AA3", "MATH 1A03", "MATH 1AA3", "CHEM 1A03"]},
    )
    assert response.status_code == 200
    results = {item["code"]: item["status"] for item in response.get_json()["results"]}

    assert results["admission-physics-3-units"] == "complete"
    assert results["admission-modern-3-units"] == "complete"
    assert results["admission-math-6-units"] == "complete"
    assert results["admission-chem-3-units"] == "complete"
    assert results["admission-bio-chem-math-3-units"] == "missing"
    assert results["gpa-minimum"] == "check-advisor"


def test_requirement_checker_partial_needs_advisor(client):
    response = client.post("/api/requirements/check", json={"courses": ["PHYSICS 1A03"]})
    results = {item["code"]: item["status"] for item in response.get_json()["results"]}

    assert results["admission-physics-3-units"] == "complete"
    assert results["admission-math-6-units"] == "missing"


def test_program_checker_level_and_track_rules(client):
    response = client.post(
        "/api/program/check",
        json={
            "courses": [
                "PHYSICS 2C03",
                "PHYSICS 2P03",
                "PHYSICS 2G03",
                "MATH 2C03",
                "MATH 2X03",
                "BIOPHYS 2S03",
                "PHYSICS 2B03",
                "PHYSICS 3K03",
                "MATH 3C03",
                "BIOPHYS 3S03",
                "MEDPHYS 4B03",
                "BIOPHYS 4S03",
                "MEDPHYS 4RA3",
                "MEDPHYS 4T03",
                "PHYSICS 3MM3",
            ]
        },
    )
    groups = response.get_json()["groups"]
    level_ii = {item["code"]: item["status"] for item in groups["level-ii"]}
    level_iii = {item["code"]: item["status"] for item in groups["level-iii"]}
    level_iv = {item["code"]: item["status"] for item in groups["level-iv"]}

    assert level_ii["level-ii-modern-lab"] == "complete"
    assert level_iii["level-iii-core"] == "complete"
    assert level_iv["level-iv-core"] == "complete"


@pytest.mark.parametrize("purpose", ["research", "coop", "grad"])
def test_cold_email_generator(client, purpose):
    response = client.post(
        "/api/cold-email",
        json={
            "purpose": purpose,
            "name": "Alex Student",
            "recipient": "Professor Chen",
            "interests": "medical imaging",
            "experience": "Python and lab coursework",
            "ask": "a short meeting",
        },
    )
    data = response.get_json()

    assert response.status_code == 200
    assert "Subject:" in data["body"]
    assert "Professor Chen" in data["body"]
    assert "Alex Student" in data["body"]
    assert "medical imaging" in data["body"]


def test_review_submission_uses_account_and_notifications(client, app):
    client.post(
        "/auth/register",
        data={
            "email": "reviewer@mcmaster.ca",
            "password": "strong-pass",
            "display_name": "Reviewer",
            "stage": "Level II",
        },
    )
    response = client.post(
        "/submit/review",
        data={
            "course_code": "PHYSICS2G03",
            "term_taken": "Winter 2026",
            "difficulty": "3",
            "workload": "3",
            "usefulness": "5",
            "math_intensity": "3",
            "coding_intensity": "5",
            "memorization_intensity": "1",
            "would_take_again": "yes",
            "advice": "Start early and keep notebooks clean.",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    with app.app_context():
        user = UserAccount.query.filter_by(email="reviewer@mcmaster.ca").one()
        review = CourseReview.query.one()
        assert review.user_id == user.id
        assert review.status == ModerationStatus.PENDING
        assert Notification.query.filter_by(user_id=user.id, category="review").count() == 1


def test_moderation_notifies_submitter_and_course_followers(client, app):
    with app.app_context():
        course = Course.query.filter_by(code="PHYSICS2G03").one()
        submitter = UserAccount(
            email="submitter@mcmaster.ca",
            password_hash="x",
            display_name="Submitter",
            stage="Level II",
            pathway_tags=[],
            goal="",
            is_mcmaster=True,
        )
        follower = UserAccount(
            email="follower@mcmaster.ca",
            password_hash="x",
            display_name="Follower",
            stage="Level II",
            pathway_tags=[],
            goal="",
            is_mcmaster=True,
        )
        db.session.add_all([submitter, follower])
        db.session.flush()
        db.session.add(UserCourseStatus(user_id=follower.id, course_id=course.id, status="planned"))
        review = CourseReview(
            course_id=course.id,
            user_id=submitter.id,
            email_private=submitter.email,
            submitter_email_hash="hash",
            status=ModerationStatus.PENDING,
            term_taken="Winter 2026",
            difficulty=3,
            workload=3,
            usefulness=5,
            math_intensity=3,
            coding_intensity=5,
            memorization_intensity=1,
            would_take_again=True,
            advice="Start early.",
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id
        submitter_id = submitter.id
        follower_id = follower.id

    with client.session_transaction() as sess:
        sess["admin"] = True
    response = client.post(f"/admin/moderate/CourseReview/{review_id}/approve")
    assert response.status_code == 302
    with app.app_context():
        assert Notification.query.filter_by(user_id=submitter_id, category="moderation").count() == 1
        assert Notification.query.filter_by(user_id=follower_id, category="course-review").count() == 1


def test_mentor_message_creates_inbox_notification(client, app):
    with app.app_context():
        mentor_user = UserAccount(
            email="mentor@mcmaster.ca",
            password_hash="x",
            display_name="Mentor User",
            stage="Alumni",
            pathway_tags=[],
            goal="",
            is_mcmaster=True,
        )
        db.session.add(mentor_user)
        db.session.flush()
        mentor = MentorProfile(
            user_id=mentor_user.id,
            display_name="Mentor",
            role_year="Alum",
            pathway_tags=["clinical medical physics"],
            experience_tags=["thesis"],
            bio="Ask me about CAMPEP.",
            contact_preference="Isocentre inbox",
            public_contact_text="Message me here",
            private_email=mentor_user.email,
            email_hash="hash",
            status=ModerationStatus.APPROVED,
        )
        db.session.add(mentor)
        db.session.commit()
        mentor_id = mentor.id
        mentor_user_id = mentor_user.id

    client.post(
        "/auth/register",
        data={
            "email": "mentee@mcmaster.ca",
            "password": "strong-pass",
            "display_name": "Mentee",
            "stage": "Level II",
        },
    )
    response = client.post(
        f"/community/mentors/{mentor_id}/message",
        data={"subject": "Research question", "body": "How should I start research outreach?"},
    )
    assert response.status_code == 302
    with app.app_context():
        message = MentorMessage.query.one()
        assert message.recipient_id == mentor_user_id
        assert Notification.query.filter_by(user_id=mentor_user_id, category="message").count() == 1


def test_mentor_directory_filters_by_tag_availability_and_dm(client, app):
    with app.app_context():
        owner = UserAccount(
            email="dmmentor@mcmaster.ca",
            password_hash="x",
            display_name="DM Mentor Owner",
            stage="Alumni",
            pathway_tags=[],
            goal="",
            is_mcmaster=True,
        )
        db.session.add(owner)
        db.session.flush()
        db.session.add_all(
            [
                MentorProfile(
                    user_id=owner.id,
                    display_name="DM CAMPEP Mentor",
                    role_year="Alum",
                    pathway_tags=["CAMPEP"],
                    experience_tags=["residency"],
                    bio="Ask about medical physics grad school.",
                    contact_preference="Isocentre inbox",
                    public_contact_text="",
                    private_email=owner.email,
                    email_hash="hash",
                    status=ModerationStatus.APPROVED,
                    mentorship_available=True,
                ),
                MentorProfile(
                    display_name="Public CAMPEP Mentor",
                    role_year="Alum",
                    pathway_tags=["CAMPEP"],
                    experience_tags=[],
                    bio="Public contact only.",
                    contact_preference="LinkedIn",
                    public_contact_text="Find me publicly",
                    private_email="public@mcmaster.ca",
                    email_hash="hash2",
                    status=ModerationStatus.APPROVED,
                    mentorship_available=True,
                ),
                MentorProfile(
                    user_id=owner.id,
                    display_name="Busy CAMPEP Mentor",
                    role_year="Alum",
                    pathway_tags=["CAMPEP"],
                    experience_tags=[],
                    bio="Busy right now.",
                    contact_preference="Isocentre inbox",
                    public_contact_text="",
                    private_email=owner.email,
                    email_hash="hash3",
                    status=ModerationStatus.APPROVED,
                    mentorship_available=False,
                ),
            ]
        )
        db.session.commit()

    response = client.get("/community/mentors?tag=CAMPEP&availability=available&contact=dm")

    assert response.status_code == 200
    assert b"DM CAMPEP Mentor" in response.data
    assert b"Public CAMPEP Mentor" not in response.data
    assert b"Busy CAMPEP Mentor" not in response.data


def test_ask_upper_year_uses_account_stage_and_notifies_higher_years(client, app):
    with app.app_context():
        lower = UserAccount(
            email="level-one@mcmaster.ca",
            password_hash="x",
            display_name="Level One",
            stage="Level I",
            pathway_tags=[],
            goal="MedBioPhys admission",
            is_mcmaster=True,
        )
        peer = UserAccount(
            email="peer@mcmaster.ca",
            password_hash="x",
            display_name="Peer",
            stage="Level I",
            pathway_tags=[],
            goal="",
            is_mcmaster=True,
        )
        upper = UserAccount(
            email="upper@mcmaster.ca",
            password_hash="x",
            display_name="Upper",
            stage="Level II",
            pathway_tags=[],
            goal="",
            is_mcmaster=True,
        )
        alum = UserAccount(
            email="alum@mcmaster.ca",
            password_hash="x",
            display_name="Alum",
            stage="Alumni",
            pathway_tags=[],
            goal="",
            is_mcmaster=True,
        )
        db.session.add_all([lower, peer, upper, alum])
        db.session.commit()
        lower_id = lower.id
        peer_id = peer.id
        upper_id = upper.id
        alum_id = alum.id

    with client.session_transaction() as sess:
        sess["user_id"] = lower_id

    response = client.post(
        "/community/ask",
        data={"stage": "Graduating", "topic": "Level II load", "body": "How should I prepare?"},
        follow_redirects=False,
    )
    assert response.status_code == 302

    with app.app_context():
        question = QuestionSubmission.query.one()
        assert question.stage == "Level I"
        assert Notification.query.filter_by(user_id=lower_id, category="question").count() == 1
        assert Notification.query.filter_by(user_id=upper_id, category="upper-year-question").count() == 1
        assert Notification.query.filter_by(user_id=alum_id, category="upper-year-question").count() == 1
        assert Notification.query.filter_by(user_id=peer_id, category="upper-year-question").count() == 0
        question_id = question.id

    with client.session_transaction() as sess:
        sess["user_id"] = upper_id
    assert client.get(f"/community/ask/{question_id}").status_code == 200
    reply = client.post(f"/community/ask/{question_id}", data={"response": "Review 1C03 and start labs early."})
    assert reply.status_code == 302
    with app.app_context():
        assert Notification.query.filter_by(user_id=lower_id, category="question-reply").count() == 1


def test_account_settings_updates_routing_profile_and_mentor_profile(client, app):
    with app.app_context():
        user = UserAccount(
            email="settings@mcmaster.ca",
            password_hash="x",
            display_name="Settings User",
            stage="Level II",
            pathway_tags=["clinical medical physics"],
            goal="Find research",
            is_mcmaster=True,
        )
        db.session.add(user)
        db.session.flush()
        mentor = MentorProfile(
            user_id=user.id,
            display_name="Settings User",
            role_year="Level II",
            pathway_tags=["clinical medical physics"],
            experience_tags=["research"],
            bio="Ask me about Level II.",
            contact_preference="Isocentre inbox",
            public_contact_text="Message me",
            private_email=user.email,
            email_hash="hash",
            status=ModerationStatus.APPROVED,
            mentorship_available=True,
        )
        db.session.add(mentor)
        db.session.commit()
        user_id = user.id
        mentor_id = mentor.id

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post(
        "/account/settings",
        data={
            "display_name": "Updated User",
            "stage": "Upper-year",
            "pathway_tags": "imaging AI, co-op",
            "goal": "Apply to CAMPEP",
            "mentor_profile_present": "yes",
            "mentor_visibility": "hidden",
            "mentor_available": "no",
            "mentor_role_year": "Upper-year co-op student",
            "mentor_pathway_tags": "imaging AI",
            "mentor_experience_tags": "co-op, thesis",
            "mentor_bio": "Ask me about imaging projects.",
            "mentor_contact_preference": "Isocentre inbox",
            "mentor_public_contact_text": "DM me here",
        },
    )
    assert response.status_code == 302

    with app.app_context():
        user = db.session.get(UserAccount, user_id)
        mentor = db.session.get(MentorProfile, mentor_id)
        assert user.stage == "Upper-year"
        assert user.pathway_tags == ["imaging AI", "co-op"]
        assert user.goal == "Apply to CAMPEP"
        assert mentor.status == ModerationStatus.HIDDEN
        assert mentor.mentorship_available is False
        assert mentor.role_year == "Upper-year co-op student"
        assert mentor.experience_tags == ["co-op", "thesis"]


def test_admin_can_create_edit_and_delete_mentor_profile(client, app):
    with app.app_context():
        owner = UserAccount(
            email="owner@mcmaster.ca",
            password_hash="x",
            display_name="Owner User",
            stage="Upper-year",
            pathway_tags=[],
            goal="",
            is_mcmaster=True,
        )
        db.session.add(owner)
        db.session.commit()

    with client.session_transaction() as sess:
        sess["admin"] = True

    create_response = client.post(
        "/admin/mentors/new",
        data={
            "owner_email": "owner@mcmaster.ca",
            "private_email": "",
            "display_name": "Admin Mentor",
            "role_year": "MSc student",
            "pathway_tags": "clinical medical physics, CAMPEP",
            "experience_tags": "thesis, grad applications",
            "bio": "Can talk about graduate school and research.",
            "contact_preference": "Isocentre inbox",
            "public_contact_text": "Message me here",
            "status": "approved",
            "mentorship_available": "yes",
            "featured": "no",
        },
        follow_redirects=False,
    )
    assert create_response.status_code == 302

    with app.app_context():
        mentor = MentorProfile.query.filter_by(display_name="Admin Mentor").one()
        mentor_id = mentor.id
        assert mentor.user.email == "owner@mcmaster.ca"
        assert mentor.status == ModerationStatus.APPROVED

    edit_response = client.post(
        f"/admin/mentors/{mentor_id}/edit",
        data={
            "owner_email": "owner@mcmaster.ca",
            "private_email": "",
            "display_name": "Edited Mentor",
            "role_year": "Medical physics resident",
            "pathway_tags": "clinical medical physics",
            "experience_tags": "CAMPEP, residency",
            "bio": "Can talk about residency applications.",
            "contact_preference": "Isocentre inbox",
            "public_contact_text": "Use Isocentre messages",
            "status": "approved",
            "mentorship_available": "yes",
            "featured": "yes",
        },
        follow_redirects=False,
    )
    assert edit_response.status_code == 302

    with app.app_context():
        mentor = db.session.get(MentorProfile, mentor_id)
        assert mentor.display_name == "Edited Mentor"
        assert mentor.featured is True

    delete_response = client.post(f"/admin/delete/MentorProfile/{mentor_id}", headers={"Referer": f"/admin/mentors/{mentor_id}/edit"}, follow_redirects=False)
    assert delete_response.status_code == 302
    assert "/admin/mentors" in delete_response.headers["Location"]
    with app.app_context():
        assert db.session.get(MentorProfile, mentor_id) is None


def test_admin_inventory_routes_require_admin_session(client):
    assert client.get("/admin/users").status_code == 403
    assert client.get("/admin/messages").status_code == 403
    with client.session_transaction() as sess:
        sess["admin"] = True
    assert client.get("/admin").status_code == 200
    assert client.get("/admin/mentors/new").status_code == 200
    assert client.get("/admin/users").status_code == 200
    assert client.get("/admin/messages").status_code == 200


def test_admin_can_delete_message_and_user_activity(client, app):
    with app.app_context():
        course = Course.query.filter_by(code="PHYSICS2G03").one()
        sender = UserAccount(
            email="delete-sender@mcmaster.ca",
            password_hash="x",
            display_name="Delete Sender",
            stage="Level II",
            pathway_tags=[],
            goal="",
            is_mcmaster=True,
        )
        recipient = UserAccount(
            email="delete-recipient@mcmaster.ca",
            password_hash="x",
            display_name="Delete Recipient",
            stage="Alumni",
            pathway_tags=[],
            goal="",
            is_mcmaster=True,
        )
        db.session.add_all([sender, recipient])
        db.session.flush()
        mentor = MentorProfile(
            user_id=recipient.id,
            display_name="Delete Mentor",
            role_year="Alum",
            pathway_tags=["clinical medical physics"],
            experience_tags=["thesis"],
            bio="Delete me.",
            contact_preference="Isocentre inbox",
            public_contact_text="",
            private_email=recipient.email,
            email_hash="hash",
            status=ModerationStatus.APPROVED,
        )
        db.session.add(mentor)
        db.session.flush()
        message = MentorMessage(mentor_id=mentor.id, sender_id=sender.id, recipient_id=recipient.id, subject="Delete message", body="body")
        review = CourseReview(
            course_id=course.id,
            user_id=sender.id,
            email_private=sender.email,
            submitter_email_hash="hash",
            status=ModerationStatus.APPROVED,
            term_taken="Winter 2026",
            difficulty=3,
            workload=3,
            usefulness=5,
            math_intensity=3,
            coding_intensity=5,
            memorization_intensity=1,
            would_take_again=True,
            advice="Delete review.",
        )
        question = QuestionSubmission(
            user_id=sender.id,
            stage="Level II",
            topic="Delete question",
            body="body",
            private_email=sender.email,
            email_hash="hash",
            status=ModerationStatus.PENDING,
        )
        db.session.add_all([message, review, question, UserCourseStatus(user_id=sender.id, course_id=course.id, status="planned")])
        db.session.flush()
        db.session.add(Notification(user_id=recipient.id, title="Message", body="body", category="message", target_type="MentorMessage", target_id=message.id))
        db.session.commit()
        message_id = message.id
        sender_id = sender.id
        recipient_id = recipient.id

    with client.session_transaction() as sess:
        sess["admin"] = True
    response = client.post(f"/admin/delete/MentorMessage/{message_id}", follow_redirects=False)
    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(MentorMessage, message_id) is None
        assert Notification.query.filter_by(target_type="MentorMessage", target_id=message_id).count() == 0

    response = client.post(f"/admin/delete/UserAccount/{sender_id}", follow_redirects=False)
    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(UserAccount, sender_id) is None
        assert CourseReview.query.filter_by(user_id=sender_id).count() == 0
        assert QuestionSubmission.query.filter_by(user_id=sender_id).count() == 0
        assert UserCourseStatus.query.filter_by(user_id=sender_id).count() == 0
        assert db.session.get(UserAccount, recipient_id) is not None
