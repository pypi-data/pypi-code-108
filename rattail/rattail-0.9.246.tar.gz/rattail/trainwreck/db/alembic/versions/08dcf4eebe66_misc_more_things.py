# -*- coding: utf-8; -*-
"""misc. more things

Revision ID: 08dcf4eebe66
Revises: 4638ceca90d6
Create Date: 2021-03-09 18:53:22.103819

"""

from __future__ import unicode_literals, absolute_import

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08dcf4eebe66'
down_revision = '4638ceca90d6'
branch_labels = None
depends_on = None


def upgrade():

    # transaction
    op.add_column('transaction', sa.Column('effective_date', sa.Date(), nullable=True))
    op.add_column('transaction', sa.Column('shopper_level_number', sa.Integer(), nullable=True))
    op.add_column('transaction', sa.Column('store_id', sa.String(length=10), nullable=True))

    # transaction_item
    op.add_column('transaction_item', sa.Column('subdepartment_name', sa.String(length=30), nullable=True))
    op.add_column('transaction_item', sa.Column('subdepartment_number', sa.Integer(), nullable=True))


def downgrade():

    # transaction_item
    op.drop_column('transaction_item', 'subdepartment_number')
    op.drop_column('transaction_item', 'subdepartment_name')

    # transaction
    op.drop_column('transaction', 'store_id')
    op.drop_column('transaction', 'shopper_level_number')
    op.drop_column('transaction', 'effective_date')
