"""user accounts and saved plans

Revision ID: 2dfb8ec18d15
Revises: 7c6c33df8211
Create Date: 2026-04-27 02:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2dfb8ec18d15"
down_revision = "7c6c33df8211"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_account",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("stage", sa.String(length=80), nullable=False),
        sa.Column("pathway_tags", sa.JSON(), nullable=False),
        sa.Column("goal", sa.String(length=180), nullable=False),
        sa.Column("is_mcmaster", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("user_account", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_user_account_email"), ["email"], unique=True)
        batch_op.create_index(batch_op.f("ix_user_account_is_mcmaster"), ["is_mcmaster"], unique=False)

    op.create_table(
        "user_course_status",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("term_label", sa.String(length=80), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["course.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user_account.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "course_id", name="uq_user_course_status"),
    )
    with op.batch_alter_table("user_course_status", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_user_course_status_course_id"), ["course_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_user_course_status_status"), ["status"], unique=False)
        batch_op.create_index(batch_op.f("ix_user_course_status_user_id"), ["user_id"], unique=False)

    op.create_table(
        "user_saved_guide",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("page_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["page_id"], ["page.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user_account.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "page_id", name="uq_user_saved_guide"),
    )
    with op.batch_alter_table("user_saved_guide", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_user_saved_guide_page_id"), ["page_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_user_saved_guide_user_id"), ["user_id"], unique=False)


def downgrade():
    with op.batch_alter_table("user_saved_guide", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_saved_guide_user_id"))
        batch_op.drop_index(batch_op.f("ix_user_saved_guide_page_id"))
    op.drop_table("user_saved_guide")

    with op.batch_alter_table("user_course_status", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_course_status_user_id"))
        batch_op.drop_index(batch_op.f("ix_user_course_status_status"))
        batch_op.drop_index(batch_op.f("ix_user_course_status_course_id"))
    op.drop_table("user_course_status")

    with op.batch_alter_table("user_account", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_account_is_mcmaster"))
        batch_op.drop_index(batch_op.f("ix_user_account_email"))
    op.drop_table("user_account")
