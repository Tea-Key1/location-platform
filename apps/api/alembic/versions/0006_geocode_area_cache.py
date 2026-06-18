"""geocode area cache

Revision ID: 0006_geocode_area_cache
Revises: 0005_similarity_check_home_coordinates
Create Date: 2026-06-18
"""

from alembic import op
import sqlalchemy as sa


revision = "0006_geocode_area_cache"
down_revision = "0005_similarity_check_home_coordinates"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "geocode_area_cache",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("s2_level12_id", sa.String(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("prefecture", sa.String(), nullable=True),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("district", sa.String(), nullable=True),
        sa.Column("country_code", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index(
        op.f("ix_geocode_area_cache_id"),
        "geocode_area_cache",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_geocode_area_cache_key"),
        "geocode_area_cache",
        ["key"],
        unique=True,
    )
    op.create_index(
        op.f("ix_geocode_area_cache_s2_level12_id"),
        "geocode_area_cache",
        ["s2_level12_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_geocode_area_cache_s2_level12_id"),
        table_name="geocode_area_cache",
    )
    op.drop_index(
        op.f("ix_geocode_area_cache_key"),
        table_name="geocode_area_cache",
    )
    op.drop_index(
        op.f("ix_geocode_area_cache_id"),
        table_name="geocode_area_cache",
    )
    op.drop_table("geocode_area_cache")
