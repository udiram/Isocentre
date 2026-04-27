"""submission queue indexes

Revision ID: 7c6c33df8211
Revises: b1da8fb37ee0
Create Date: 2026-04-27 02:20:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "7c6c33df8211"
down_revision = "b1da8fb37ee0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_course_review_status_created_at", "course_review", ["status", "created_at"], unique=False)
    op.create_index("ix_course_review_course_status_created_at", "course_review", ["course_id", "status", "created_at"], unique=False)
    op.create_index("ix_mentor_profile_status_created_at", "mentor_profile", ["status", "created_at"], unique=False)
    op.create_index("ix_mentor_profile_status_featured_updated_at", "mentor_profile", ["status", "featured", "updated_at"], unique=False)
    op.create_index("ix_question_submission_status_created_at", "question_submission", ["status", "created_at"], unique=False)
    op.create_index("ix_email_verification_token_email_created_at", "email_verification_token", ["email", "created_at"], unique=False)
    op.create_index("ix_admin_audit_log_target_created_at", "admin_audit_log", ["target_type", "target_id", "created_at"], unique=False)


def downgrade():
    op.drop_index("ix_admin_audit_log_target_created_at", table_name="admin_audit_log")
    op.drop_index("ix_email_verification_token_email_created_at", table_name="email_verification_token")
    op.drop_index("ix_question_submission_status_created_at", table_name="question_submission")
    op.drop_index("ix_mentor_profile_status_featured_updated_at", table_name="mentor_profile")
    op.drop_index("ix_mentor_profile_status_created_at", table_name="mentor_profile")
    op.drop_index("ix_course_review_course_status_created_at", table_name="course_review")
    op.drop_index("ix_course_review_status_created_at", table_name="course_review")
