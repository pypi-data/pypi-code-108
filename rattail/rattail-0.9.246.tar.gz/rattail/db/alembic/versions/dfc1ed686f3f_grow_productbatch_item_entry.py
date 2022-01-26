# -*- coding: utf-8; -*-
"""grow ProductBatch.item_entry

Revision ID: dfc1ed686f3f
Revises: 9ec8deec5256
Create Date: 2020-03-01 14:14:22.198396

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'dfc1ed686f3f'
down_revision = '9ec8deec5256'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch*
    op.alter_column('batch_handheld_row', 'item_entry', type_=sa.String(length=32))
    op.alter_column('batch_inventory_row', 'item_entry', type_=sa.String(length=32))
    op.alter_column('batch_newproduct_row', 'item_entry', type_=sa.String(length=32))
    op.alter_column('batch_pricing_row', 'item_entry', type_=sa.String(length=32))
    op.alter_column('batch_product_row', 'item_entry', type_=sa.String(length=32))
    op.alter_column('label_batch_row', 'item_entry', type_=sa.String(length=32))
    op.alter_column('purchase_batch_row', 'item_entry', type_=sa.String(length=32))
    op.alter_column('vendor_catalog_row', 'item_entry', type_=sa.String(length=32))
    op.alter_column('vendor_invoice_row', 'item_entry', type_=sa.String(length=32))


def downgrade():

    # batch*
    op.alter_column('vendor_invoice_row', 'item_entry', type_=sa.String(length=20))
    op.alter_column('vendor_catalog_row', 'item_entry', type_=sa.String(length=20))
    op.alter_column('purchase_batch_row', 'item_entry', type_=sa.String(length=20))
    op.alter_column('label_batch_row', 'item_entry', type_=sa.String(length=20))
    op.alter_column('batch_product_row', 'item_entry', type_=sa.String(length=20))
    op.alter_column('batch_pricing_row', 'item_entry', type_=sa.String(length=20))
    op.alter_column('batch_newproduct_row', 'item_entry', type_=sa.String(length=20))
    op.alter_column('batch_inventory_row', 'item_entry', type_=sa.String(length=20))
    op.alter_column('batch_handheld_row', 'item_entry', type_=sa.String(length=20))
