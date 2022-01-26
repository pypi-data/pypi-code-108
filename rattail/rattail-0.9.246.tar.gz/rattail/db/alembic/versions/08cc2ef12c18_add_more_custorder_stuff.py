# -*- coding: utf-8; -*-
"""add more custorder stuff

Revision ID: 08cc2ef12c18
Revises: 3f3523703313
Create Date: 2021-12-21 17:00:11.841243

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '08cc2ef12c18'
down_revision = '3f3523703313'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # pending_product
    op.add_column('pending_product', sa.Column('vendor_name', sa.String(length=50), nullable=True))
    op.add_column('pending_product', sa.Column('vendor_uuid', sa.String(length=32), nullable=True))
    op.add_column('pending_product', sa.Column('vendor_item_code', sa.String(length=20), nullable=True))
    op.add_column('pending_product', sa.Column('unit_cost', sa.Numeric(precision=10, scale=5), nullable=True))
    op.create_foreign_key('pending_product_fk_vendor', 'pending_product', 'vendor', ['vendor_uuid'], ['uuid'])

    # batch_custorder_row
    op.add_column('batch_custorder_row', sa.Column('pending_product_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key('batch_custorder_row_fk_pending_product', 'batch_custorder_row', 'pending_product', ['pending_product_uuid'], ['uuid'])
    op.add_column('batch_custorder_row', sa.Column('unit_regular_price', sa.Numeric(precision=8, scale=3), nullable=True))
    op.add_column('batch_custorder_row', sa.Column('unit_sale_price', sa.Numeric(precision=8, scale=3), nullable=True))
    op.add_column('batch_custorder_row', sa.Column('sale_ends', sa.DateTime(), nullable=True))
    op.add_column('batch_custorder_row', sa.Column('product_scancode', sa.String(length=14), nullable=True))
    op.add_column('batch_custorder_row', sa.Column('product_item_id', sa.String(length=50), nullable=True))

    # custorder_item
    op.add_column('custorder_item', sa.Column('pending_product_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key('custorder_item_fk_pending_product', 'custorder_item', 'pending_product', ['pending_product_uuid'], ['uuid'])
    op.add_column('custorder_item', sa.Column('unit_regular_price', sa.Numeric(precision=8, scale=3), nullable=True))
    op.add_column('custorder_item', sa.Column('unit_sale_price', sa.Numeric(precision=8, scale=3), nullable=True))
    op.add_column('custorder_item', sa.Column('sale_ends', sa.DateTime(), nullable=True))
    op.add_column('custorder_item', sa.Column('product_scancode', sa.String(length=14), nullable=True))
    op.add_column('custorder_item', sa.Column('product_item_id', sa.String(length=50), nullable=True))


def downgrade():

    # custorder_item
    op.drop_column('custorder_item', 'product_item_id')
    op.drop_column('custorder_item', 'product_scancode')
    op.drop_column('custorder_item', 'sale_ends')
    op.drop_column('custorder_item', 'unit_sale_price')
    op.drop_column('custorder_item', 'unit_regular_price')
    op.drop_constraint('custorder_item_fk_pending_product', 'custorder_item', type_='foreignkey')
    op.drop_column('custorder_item', 'pending_product_uuid')

    # batch_custorder_row
    op.drop_column('batch_custorder_row', 'product_item_id')
    op.drop_column('batch_custorder_row', 'product_scancode')
    op.drop_column('batch_custorder_row', 'sale_ends')
    op.drop_column('batch_custorder_row', 'unit_sale_price')
    op.drop_column('batch_custorder_row', 'unit_regular_price')
    op.drop_constraint('batch_custorder_row_fk_pending_product', 'batch_custorder_row', type_='foreignkey')
    op.drop_column('batch_custorder_row', 'pending_product_uuid')

    # pending_product
    op.drop_constraint('pending_product_fk_vendor', 'pending_product', type_='foreignkey')
    op.drop_column('pending_product', 'unit_cost')
    op.drop_column('pending_product', 'vendor_item_code')
    op.drop_column('pending_product', 'vendor_uuid')
    op.drop_column('pending_product', 'vendor_name')
