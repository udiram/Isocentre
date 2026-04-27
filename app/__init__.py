import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    raw_database_url = os.getenv("DATABASE_URL")
    if is_railway_runtime() and (not raw_database_url or raw_database_url.startswith("sqlite")):
        raise RuntimeError("DATABASE_URL must be set to Railway Postgres. Refusing to run Railway with SQLite.")
    database_url = normalize_database_url(raw_database_url or "sqlite:///:memory:")
    resend_api_key = os.getenv("RESEND_API_KEY", "")
    engine_options = {}
    if database_url.startswith("postgresql"):
        engine_options = {
            "pool_pre_ping": True,
            "pool_recycle": 280,
            "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "5")),
        }
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-me"),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS=engine_options,
        ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD", ""),
        RESEND_API_KEY=resend_api_key,
        MAIL_SERVER=os.getenv("MAIL_SERVER") or ("smtp.resend.com" if resend_api_key else ""),
        MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
        MAIL_USERNAME=os.getenv("MAIL_USERNAME") or ("resend" if resend_api_key else ""),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD") or resend_api_key,
        MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER")
        or os.getenv("RESEND_FROM_EMAIL")
        or ("Isocentre <onboarding@resend.dev>" if resend_api_key else ""),
        MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "true").lower() != "false",
        SITE_BASE_URL=os.getenv("SITE_BASE_URL", "http://127.0.0.1:5000"),
        GOOGLE_ANALYTICS_ID=os.getenv("GOOGLE_ANALYTICS_ID", "G-KZ430V2G5C"),
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", str(24 * 1024 * 1024))),
        MESSAGE_ATTACHMENT_MAX_BYTES=int(os.getenv("MESSAGE_ATTACHMENT_MAX_BYTES", str(8 * 1024 * 1024))),
        MESSAGE_ATTACHMENT_MAX_COUNT=int(os.getenv("MESSAGE_ATTACHMENT_MAX_COUNT", "4")),
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # noqa: F401
    from .routes import bp
    from .seed import seed_database

    app.register_blueprint(bp)

    @app.cli.command("seed")
    def seed_command():
        """Seed database content for the Isocentre MVP."""
        seed_database(db.session)
        db.session.commit()
        print("Seeded Isocentre content.")

    @app.cli.command("init-db")
    def init_db_command():
        """Create tables and seed content without Alembic, useful for first Railway bootstraps."""
        db.create_all()
        seed_database(db.session)
        db.session.commit()
        print("Initialized and seeded Isocentre database.")

    return app


def normalize_database_url(url):
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


def is_railway_runtime():
    return any(os.getenv(name) for name in ("RAILWAY_ENVIRONMENT", "RAILWAY_PROJECT_ID", "RAILWAY_SERVICE_ID"))
