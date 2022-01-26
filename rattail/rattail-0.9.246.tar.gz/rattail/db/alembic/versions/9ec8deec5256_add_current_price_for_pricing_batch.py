# -*- coding: utf-8; -*-
"""add current_price for pricing batch

Revision ID: 9ec8deec5256
Revises: 4ff1a9a97b4e
Create Date: 2020-02-07 17:46:15.020584

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '9ec8deec5256'
down_revision = '4ff1a9a97b4e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_pricing_row
    op.add_column('batch_pricing_row', sa.Column('current_price', sa.Numeric(precision=8, scale=3), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('current_price_ends', sa.DateTime(), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('current_price_starts', sa.DateTime(), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('current_price_type', sa.Integer(), nullable=True))


def downgrade():

    # batch_pricing_row
    op.drop_column('batch_pricing_row', 'current_price_type')
    op.drop_column('batch_pricing_row', 'current_price_starts')
    op.drop_column('batch_pricing_row', 'current_price_ends')
    op.drop_column('batch_pricing_row', 'current_price')
