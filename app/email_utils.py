import hashlib
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from secrets import token_urlsafe

from flask import current_app, url_for

from .models import EmailVerificationToken


def normalize_email(email):
    return " ".join(str(email).strip().lower().split())


def is_mcmaster_email(email):
    return normalize_email(email).endswith("@mcmaster.ca")


def email_hash(email):
    secret = current_app.config["SECRET_KEY"]
    return hashlib.sha256(f"{secret}:{normalize_email(email)}".encode("utf-8")).hexdigest()


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_verification_token(session, email, purpose, target_type, target_id):
    token = token_urlsafe(32)
    record = EmailVerificationToken(
        email=normalize_email(email),
        purpose=purpose,
        target_type=target_type,
        target_id=target_id,
        token_hash=hash_token(token),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    session.add(record)
    return token


def send_verification_email(email, token):
    verify_url = current_app.config["SITE_BASE_URL"].rstrip("/") + url_for("main.verify_email", token=token)
    subject = "Verify your Isocentre submission"
    body = (
        "Click this link within 24 hours to verify your McMaster email and send your Isocentre "
        f"submission to moderation:\n\n{verify_url}\n\n"
        "If you did not submit anything to Isocentre, ignore this email."
    )

    if not current_app.config.get("MAIL_SERVER"):
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    message["To"] = email
    message.set_content(body)

    try:
        with smtplib.SMTP(current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"], timeout=15) as smtp:
            if current_app.config["MAIL_USE_TLS"]:
                smtp.starttls()
            if current_app.config["MAIL_USERNAME"]:
                smtp.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        current_app.logger.warning("Verification email could not be sent: %s", exc)
        return False
    return True
