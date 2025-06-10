"""Add status column to DebateTopic

Revision ID: 0879a5f820cf
Revises: 2d9951150b46
Create Date: 2025-05-14 23:22:36.910235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0879a5f820cf'
down_revision = '2d9951150b46'
branch_labels = None
depends_on = None


def upgrade():
    # Only add the `status` column to the `debate_topic` table
    op.add_column('debate_topic', sa.Column('status', sa.String(length=20), nullable=True))


def downgrade():
    # Remove the `status` column from the `debate_topic` table
    op.drop_column('debate_topic', 'status')
