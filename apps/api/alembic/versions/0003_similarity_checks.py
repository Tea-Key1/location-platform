"""similarity checks

Revision ID: 0003_similarity_checks
Revises: 0002_tracking_consent
Create Date: 2026-06-13
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_similarity_checks"
down_revision = "0002_tracking_consent"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "similarity_checks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("similarity", sa.Float(), nullable=False),
        sa.Column("home_prefecture", sa.String(), nullable=True),
        sa.Column("home_city", sa.String(), nullable=True),
        sa.Column("home_district", sa.String(), nullable=True),
        sa.Column("current_prefecture", sa.String(), nullable=True),
        sa.Column("current_city", sa.String(), nullable=True),
        sa.Column("current_district", sa.String(), nullable=True),
        sa.Column("current_lat", sa.Float(), nullable=False),
        sa.Column("current_lng", sa.Float(), nullable=False),
        sa.Column("current_s2_id", sa.String(), nullable=False),
        sa.Column(
            "commercial_tracking_allowed_at_collection",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column(
            "tracking_consent_status_at_collection",
            sa.String(),
            server_default="not_determined",
            nullable=False,
        ),
        sa.Column("checked_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_similarity_checks_checked_at"),
        "similarity_checks",
        ["checked_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_similarity_checks_commercial_tracking_allowed_at_collection"),
        "similarity_checks",
        ["commercial_tracking_allowed_at_collection"],
        unique=False,
    )
    op.create_index(
        op.f("ix_similarity_checks_current_city"),
        "similarity_checks",
        ["current_city"],
        unique=False,
    )
    op.create_index(
        op.f("ix_similarity_checks_current_district"),
        "similarity_checks",
        ["current_district"],
        unique=False,
    )
    op.create_index(
        op.f("ix_similarity_checks_current_prefecture"),
        "similarity_checks",
        ["current_prefecture"],
        unique=False,
    )
    op.create_index(
        op.f("ix_similarity_checks_current_s2_id"),
        "similarity_checks",
        ["current_s2_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_similarity_checks_id"),
        "similarity_checks",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_similarity_checks_user_id"),
        "similarity_checks",
        ["user_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_similarity_checks_user_id"),
        table_name="similarity_checks",
    )
    op.drop_index(
        op.f("ix_similarity_checks_id"),
        table_name="similarity_checks",
    )
    op.drop_index(
        op.f("ix_similarity_checks_current_s2_id"),
        table_name="similarity_checks",
    )
    op.drop_index(
        op.f("ix_similarity_checks_current_prefecture"),
        table_name="similarity_checks",
    )
    op.drop_index(
        op.f("ix_similarity_checks_current_district"),
        table_name="similarity_checks",
    )
    op.drop_index(
        op.f("ix_similarity_checks_current_city"),
        table_name="similarity_checks",
    )
    op.drop_index(
        op.f("ix_similarity_checks_commercial_tracking_allowed_at_collection"),
        table_name="similarity_checks",
    )
    op.drop_index(
        op.f("ix_similarity_checks_checked_at"),
        table_name="similarity_checks",
    )
    op.drop_table("similarity_checks")
