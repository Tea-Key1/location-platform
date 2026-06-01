"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-01
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("apple_sub", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("gender", sa.String(), nullable=True),
        sa.Column("age_range", sa.String(), nullable=True),
        sa.Column("calm", sa.Float(), nullable=True),
        sa.Column("vivid", sa.Float(), nullable=True),
        sa.Column("roamer", sa.Float(), nullable=True),
        sa.Column("luxury", sa.Float(), nullable=True),
        sa.Column("nature", sa.Float(), nullable=True),
        sa.Column("nightlife", sa.Float(), nullable=True),
        sa.Column("local", sa.Float(), nullable=True),
        sa.Column("creative", sa.Float(), nullable=True),
        sa.Column("home_lat", sa.Float(), nullable=True),
        sa.Column("home_lng", sa.Float(), nullable=True),
        sa.Column("profile_completed", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(
        op.f("ix_users_apple_sub"),
        "users",
        ["apple_sub"],
        unique=True,
    )

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("jti", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_auth_sessions_expires_at"),
        "auth_sessions",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_auth_sessions_id"),
        "auth_sessions",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_auth_sessions_jti"),
        "auth_sessions",
        ["jti"],
        unique=True,
    )
    op.create_index(
        op.f("ix_auth_sessions_revoked_at"),
        "auth_sessions",
        ["revoked_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_auth_sessions_user_id"),
        "auth_sessions",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("accuracy", sa.Float(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("s2_level12_id", sa.String(), nullable=False),
        sa.Column("prefecture", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("locality", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_locations_id"), "locations", ["id"], unique=False)
    op.create_index(
        op.f("ix_locations_s2_level12_id"),
        "locations",
        ["s2_level12_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_locations_timestamp"),
        "locations",
        ["timestamp"],
        unique=False,
    )
    op.create_index(
        op.f("ix_locations_user_id"),
        "locations",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("age_group", sa.String(), nullable=True),
        sa.Column("gender", sa.String(), nullable=True),
        sa.Column("home_lat", sa.Float(), nullable=True),
        sa.Column("home_lng", sa.Float(), nullable=True),
        sa.Column("calm", sa.Float(), nullable=True),
        sa.Column("vivid", sa.Float(), nullable=True),
        sa.Column("roamer", sa.Float(), nullable=True),
        sa.Column("luxury", sa.Float(), nullable=True),
        sa.Column("nature", sa.Float(), nullable=True),
        sa.Column("nightlife", sa.Float(), nullable=True),
        sa.Column("local", sa.Float(), nullable=True),
        sa.Column("creative", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_profiles_id"), "profiles", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_profiles_id"), table_name="profiles")
    op.drop_table("profiles")
    op.drop_index(op.f("ix_locations_user_id"), table_name="locations")
    op.drop_index(op.f("ix_locations_timestamp"), table_name="locations")
    op.drop_index(op.f("ix_locations_s2_level12_id"), table_name="locations")
    op.drop_index(op.f("ix_locations_id"), table_name="locations")
    op.drop_table("locations")
    op.drop_index(op.f("ix_auth_sessions_user_id"), table_name="auth_sessions")
    op.drop_index(op.f("ix_auth_sessions_revoked_at"), table_name="auth_sessions")
    op.drop_index(op.f("ix_auth_sessions_jti"), table_name="auth_sessions")
    op.drop_index(op.f("ix_auth_sessions_id"), table_name="auth_sessions")
    op.drop_index(op.f("ix_auth_sessions_expires_at"), table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_index(op.f("ix_users_apple_sub"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
