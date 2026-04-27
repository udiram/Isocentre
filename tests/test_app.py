import pytest

from app import create_app, db
from app.models import (
    Course,
    CourseReview,
    MentorMessage,
    MentorProfile,
    ModerationStatus,
    Notification,
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
        if route in {"/notifications", "/messages"}:
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
