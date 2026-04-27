"""message attachments

Revision ID: 9a76c4e22d9a
Revises: cb9f5d8a1a77
Create Date: 2026-04-27 20:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "9a76c4e22d9a"
down_revision = "cb9f5d8a1a77"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mentor_message_attachment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["message_id"], ["mentor_message.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("mentor_message_attachment", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_mentor_message_attachment_message_id"), ["message_id"], unique=False)


def downgrade():
    with op.batch_alter_table("mentor_message_attachment", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_mentor_message_attachment_message_id"))
    op.drop_table("mentor_message_attachment")
