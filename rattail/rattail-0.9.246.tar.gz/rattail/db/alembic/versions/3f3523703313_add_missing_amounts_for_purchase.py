# -*- coding: utf-8 -*-
"""add 'missing' amounts for purchase

Revision ID: 3f3523703313
Revises: 24577b3bda93
Create Date: 2021-12-12 15:06:09.873087

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '3f3523703313'
down_revision = '24577b3bda93'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_item
    op.add_column('purchase_item', sa.Column('cases_missing', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('purchase_item', sa.Column('units_missing', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('purchase_item', sa.Column('po_case_size', sa.Numeric(precision=8, scale=2), nullable=True))
    op.add_column('purchase_item', sa.Column('invoice_case_size', sa.Numeric(precision=8, scale=2), nullable=True))

    # batch_purchase_row
    op.add_column('batch_purchase_row', sa.Column('cases_missing', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('batch_purchase_row', sa.Column('units_missing', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('batch_purchase_row', sa.Column('po_case_size', sa.Numeric(precision=8, scale=2), nullable=True))
    op.add_column('batch_purchase_row', sa.Column('invoice_case_size', sa.Numeric(precision=8, scale=2), nullable=True))


def downgrade():

    # batch_purchase_row
    op.drop_column('batch_purchase_row', 'units_missing')
    op.drop_column('batch_purchase_row', 'cases_missing')
    op.drop_column('batch_purchase_row', 'invoice_case_size')
    op.drop_column('batch_purchase_row', 'po_case_size')

    # purchase_item
    op.drop_column('purchase_item', 'units_missing')
    op.drop_column('purchase_item', 'cases_missing')
    op.drop_column('purchase_item', 'invoice_case_size')
    op.drop_column('purchase_item', 'po_case_size')
