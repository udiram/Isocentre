"""in app notifications and messages

Revision ID: cb9f5d8a1a77
Revises: 2dfb8ec18d15
Create Date: 2026-04-27 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "cb9f5d8a1a77"
down_revision = "2dfb8ec18d15"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("course_review", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_course_review_user_id_user_account", "user_account", ["user_id"], ["id"])
        batch_op.create_index(batch_op.f("ix_course_review_user_id"), ["user_id"], unique=False)

    with op.batch_alter_table("mentor_profile", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_mentor_profile_user_id_user_account", "user_account", ["user_id"], ["id"])
        batch_op.create_index(batch_op.f("ix_mentor_profile_user_id"), ["user_id"], unique=False)

    with op.batch_alter_table("question_submission", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_question_submission_user_id_user_account", "user_account", ["user_id"], ["id"])
        batch_op.create_index(batch_op.f("ix_question_submission_user_id"), ["user_id"], unique=False)

    op.create_table(
        "notification",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("link_url", sa.String(length=500), nullable=False),
        sa.Column("actor_label", sa.String(length=120), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user_account.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("notification", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_notification_category"), ["category"], unique=False)
        batch_op.create_index(batch_op.f("ix_notification_read_at"), ["read_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_notification_target_id"), ["target_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_notification_target_type"), ["target_type"], unique=False)
        batch_op.create_index(batch_op.f("ix_notification_user_id"), ["user_id"], unique=False)

    op.create_table(
        "mentor_message",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mentor_id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(length=180), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["mentor_id"], ["mentor_profile.id"]),
        sa.ForeignKeyConstraint(["recipient_id"], ["user_account.id"]),
        sa.ForeignKeyConstraint(["sender_id"], ["user_account.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("mentor_message", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_mentor_message_mentor_id"), ["mentor_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_mentor_message_read_at"), ["read_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_mentor_message_recipient_id"), ["recipient_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_mentor_message_sender_id"), ["sender_id"], unique=False)


def downgrade():
    with op.batch_alter_table("mentor_message", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_mentor_message_sender_id"))
        batch_op.drop_index(batch_op.f("ix_mentor_message_recipient_id"))
        batch_op.drop_index(batch_op.f("ix_mentor_message_read_at"))
        batch_op.drop_index(batch_op.f("ix_mentor_message_mentor_id"))
    op.drop_table("mentor_message")

    with op.batch_alter_table("notification", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_notification_user_id"))
        batch_op.drop_index(batch_op.f("ix_notification_target_type"))
        batch_op.drop_index(batch_op.f("ix_notification_target_id"))
        batch_op.drop_index(batch_op.f("ix_notification_read_at"))
        batch_op.drop_index(batch_op.f("ix_notification_category"))
    op.drop_table("notification")

    with op.batch_alter_table("question_submission", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_question_submission_user_id"))
        batch_op.drop_constraint("fk_question_submission_user_id_user_account", type_="foreignkey")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("mentor_profile", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_mentor_profile_user_id"))
        batch_op.drop_constraint("fk_mentor_profile_user_id_user_account", type_="foreignkey")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("course_review", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_course_review_user_id"))
        batch_op.drop_constraint("fk_course_review_user_id_user_account", type_="foreignkey")
        batch_op.drop_column("user_id")
