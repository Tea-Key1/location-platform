"""similarity check source

Revision ID: 0004_similarity_check_source
Revises: 0003_similarity_checks
Create Date: 2026-06-17
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_similarity_check_source"
down_revision = "0003_similarity_checks"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "similarity_checks",
        sa.Column("source", sa.String(), nullable=True),
    )


def downgrade():
    op.drop_column("similarity_checks", "source")
