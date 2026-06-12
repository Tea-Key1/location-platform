"""tracking consent

Revision ID: 0002_tracking_consent
Revises: 0001_initial_schema
Create Date: 2026-06-13
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_tracking_consent"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "tracking_authorized",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "tracking_status",
            sa.String(),
            server_default="not_determined",
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column("tracking_updated_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("tracking_source", sa.String(), nullable=True),
    )

    op.add_column(
        "locations",
        sa.Column(
            "commercial_tracking_allowed_at_collection",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.add_column(
        "locations",
        sa.Column(
            "tracking_consent_status_at_collection",
            sa.String(),
            server_default="not_determined",
            nullable=False,
        ),
    )
    op.create_index(
        op.f("ix_locations_commercial_tracking_allowed_at_collection"),
        "locations",
        ["commercial_tracking_allowed_at_collection"],
        unique=False,
    )

    op.create_table(
        "tracking_consent_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("old_status", sa.String(), nullable=True),
        sa.Column("new_status", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("changed_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_tracking_consent_audit_logs_changed_at"),
        "tracking_consent_audit_logs",
        ["changed_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tracking_consent_audit_logs_id"),
        "tracking_consent_audit_logs",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tracking_consent_audit_logs_user_id"),
        "tracking_consent_audit_logs",
        ["user_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_tracking_consent_audit_logs_user_id"),
        table_name="tracking_consent_audit_logs",
    )
    op.drop_index(
        op.f("ix_tracking_consent_audit_logs_id"),
        table_name="tracking_consent_audit_logs",
    )
    op.drop_index(
        op.f("ix_tracking_consent_audit_logs_changed_at"),
        table_name="tracking_consent_audit_logs",
    )
    op.drop_table("tracking_consent_audit_logs")
    op.drop_index(
        op.f("ix_locations_commercial_tracking_allowed_at_collection"),
        table_name="locations",
    )
    op.drop_column("locations", "tracking_consent_status_at_collection")
    op.drop_column("locations", "commercial_tracking_allowed_at_collection")
    op.drop_column("users", "tracking_source")
    op.drop_column("users", "tracking_updated_at")
    op.drop_column("users", "tracking_status")
    op.drop_column("users", "tracking_authorized")
