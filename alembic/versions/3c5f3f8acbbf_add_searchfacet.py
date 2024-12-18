"""add SearchFacet

Revision ID: 3c5f3f8acbbf
Revises: a6e3f163a9ec
Create Date: 2024-11-10 01:04:33.633691

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3c5f3f8acbbf'
down_revision: Union[str, None] = 'a6e3f163a9ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('search_facets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('facet_name', sa.String(), nullable=True),
    sa.Column('facet_parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('facet_hash', sa.String(), nullable=True),
    sa.Column('facet_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('search_facets')
    # ### end Alembic commands ###
