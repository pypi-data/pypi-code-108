# -*- coding: utf-8 -*-
"""add Member.number

Revision ID: be2cb8322066
Revises: dfc1ed686f3f
Create Date: 2020-03-18 12:25:28.386086

"""

# revision identifiers, used by Alembic.
revision = 'be2cb8322066'
down_revision = 'dfc1ed686f3f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # member
    op.add_column('member', sa.Column('number', sa.Integer(), nullable=True))
    op.add_column('member_version', sa.Column('number', sa.Integer(), autoincrement=False, nullable=True))


def downgrade():

    # member
    op.drop_column('member_version', 'number')
    op.drop_column('member', 'number')
