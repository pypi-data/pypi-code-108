# -*- coding: utf-8; -*-
"""add catalog cost for receiving

Revision ID: fd0975329091
Revises: e838d0b930fc
Create Date: 2019-11-22 19:42:24.126125

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'fd0975329091'
down_revision = 'e838d0b930fc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch_row
    op.add_column('purchase_batch_row', sa.Column('catalog_cost_confirmed', sa.Boolean(), nullable=True))
    op.add_column('purchase_batch_row', sa.Column('catalog_unit_cost', sa.Numeric(precision=7, scale=3), nullable=True))
    op.add_column('purchase_batch_row', sa.Column('invoice_cost_confirmed', sa.Boolean(), nullable=True))

    # purchase_item
    op.add_column('purchase_item', sa.Column('catalog_unit_cost', sa.Numeric(precision=7, scale=3), nullable=True))


def downgrade():

    # purchase_item
    op.drop_column('purchase_item', 'catalog_unit_cost')

    # purchase_batch_row
    op.drop_column('purchase_batch_row', 'invoice_cost_confirmed')
    op.drop_column('purchase_batch_row', 'catalog_unit_cost')
    op.drop_column('purchase_batch_row', 'catalog_cost_confirmed')
