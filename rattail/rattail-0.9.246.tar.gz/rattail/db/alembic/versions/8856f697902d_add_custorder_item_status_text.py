# -*- coding: utf-8 -*-
"""add custorder_item.status_text

Revision ID: 8856f697902d
Revises: 8b78ef45a36c
Create Date: 2021-10-18 11:51:34.326750

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '8856f697902d'
down_revision = '8b78ef45a36c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # custorder_item
    op.add_column('custorder_item', sa.Column('price_needs_confirmation', sa.Boolean(), nullable=True))
    op.add_column('custorder_item', sa.Column('status_text', sa.String(length=255), nullable=True))

    # batch_custorder_row
    op.add_column('batch_custorder_row', sa.Column('price_needs_confirmation', sa.Boolean(), nullable=True))


def downgrade():

    # batch_custorder_row
    op.drop_column('batch_custorder_row', 'price_needs_confirmation')

    # custorder_item
    op.drop_column('custorder_item', 'status_text')
    op.drop_column('custorder_item', 'price_needs_confirmation')
