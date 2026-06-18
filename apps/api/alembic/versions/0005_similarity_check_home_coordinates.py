"""similarity check home coordinates

Revision ID: 0005_similarity_check_home_coordinates
Revises: 0004_similarity_check_source
Create Date: 2026-06-18
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_similarity_check_home_coordinates"
down_revision = "0004_similarity_check_source"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "similarity_checks",
        sa.Column("home_lat", sa.Float(), nullable=True),
    )
    op.add_column(
        "similarity_checks",
        sa.Column("home_lng", sa.Float(), nullable=True),
    )


def downgrade():
    op.drop_column("similarity_checks", "home_lng")
    op.drop_column("similarity_checks", "home_lat")
