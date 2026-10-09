"""1_init_city_stree_market

Revision ID: 4f976b244281
Revises: 
Create Date: 2026-10-08 20:03:17.508718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f976b244281'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'cities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'streets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('city_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'markets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('street_id', sa.Integer(), nullable=False),
        sa.Column('house_number', sa.String(length=255), nullable=False),
        sa.Column('opening_time', sa.Time(), nullable=False),
        sa.Column('closing_time', sa.Time(), nullable=False),
        sa.ForeignKeyConstraint(['street_id'], ['streets.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('markets')
    op.drop_table('streets')
    op.drop_table('cities')
