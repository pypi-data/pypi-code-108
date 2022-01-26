# -*- coding: utf-8; -*-
"""rename batch_purchase

Revision ID: 82d3c2d9830d
Revises: 6b06ebea979c
Create Date: 2021-02-02 15:34:14.574117

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '82d3c2d9830d'
down_revision = '6b06ebea979c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # purchase
    op.drop_constraint('purchase_purchase_fk_buyer', 'purchase', type_='foreignkey')
    op.create_foreign_key('purchase_fk_buyer',
                          'purchase', 'employee',
                          ['buyer_uuid'], ['uuid'])

    # remove references to `purchase_batch`
    op.drop_constraint('purchase_batch_row_fk_batch_uuid', 'purchase_batch_row', type_='foreignkey')

    # batch_purchase
    op.drop_constraint('purchase_batch_fk_created_by', 'purchase_batch', type_='foreignkey')
    op.drop_constraint('purchase_batch_fk_cognized_by', 'purchase_batch', type_='foreignkey')
    op.drop_constraint('purchase_batch_fk_executed_by', 'purchase_batch', type_='foreignkey')
    op.drop_constraint('purchase_batch_fk_store', 'purchase_batch', type_='foreignkey')
    op.drop_constraint('purchase_batch_fk_vendor', 'purchase_batch', type_='foreignkey')
    op.drop_constraint('purchase_batch_fk_department', 'purchase_batch', type_='foreignkey')
    op.drop_constraint('purchase_batch_purchase_fk_buyer', 'purchase_batch', type_='foreignkey')
    op.drop_constraint('purchase_batch_fk_purchase', 'purchase_batch', type_='foreignkey')
    op.drop_constraint('purchase_batch_fk_truck_dump_batch', 'purchase_batch', type_='foreignkey')
    op.rename_table('purchase_batch', 'batch_purchase')
    op.create_foreign_key('batch_purchase_fk_created_by',
                          'batch_purchase', 'user',
                          ['created_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_fk_cognized_by',
                          'batch_purchase', 'user',
                          ['cognized_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_fk_executed_by',
                          'batch_purchase', 'user',
                          ['executed_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_fk_store',
                          'batch_purchase', 'store',
                          ['store_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_fk_vendor',
                          'batch_purchase', 'vendor',
                          ['vendor_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_fk_department',
                          'batch_purchase', 'department',
                          ['department_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_fk_buyer',
                          'batch_purchase', 'employee',
                          ['buyer_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_fk_purchase',
                          'batch_purchase', 'purchase',
                          ['purchase_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_fk_truck_dump_batch',
                          'batch_purchase', 'batch_purchase',
                          ['truck_dump_batch_uuid'], ['uuid'])

    # batch_purchase_row
    op.drop_constraint('purchase_batch_row_fk_product', 'purchase_batch_row', type_='foreignkey')
    op.drop_constraint('purchase_batch_row_fk_item', 'purchase_batch_row', type_='foreignkey')
    op.rename_table('purchase_batch_row', 'batch_purchase_row')
    op.create_foreign_key('batch_purchase_row_fk_batch_uuid',
                          'batch_purchase_row', 'batch_purchase',
                          ['batch_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_row_fk_product',
                          'batch_purchase_row', 'product',
                          ['product_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_row_fk_item',
                          'batch_purchase_row', 'purchase_item',
                          ['item_uuid'], ['uuid'])

    # batch_purchase_row_claim
    op.drop_constraint('purchase_batch_row_claim_fk_claiming_row', 'purchase_batch_row_claim', type_='foreignkey')
    op.drop_constraint('purchase_batch_row_claim_fk_claimed_row', 'purchase_batch_row_claim', type_='foreignkey')
    op.rename_table('purchase_batch_row_claim', 'batch_purchase_row_claim')
    op.create_foreign_key('batch_purchase_row_claim_fk_claiming_row',
                          'batch_purchase_row_claim', 'batch_purchase_row',
                          ['claiming_row_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_row_claim_fk_claimed_row',
                          'batch_purchase_row_claim', 'batch_purchase_row',
                          ['claimed_row_uuid'], ['uuid'])

    # batch_purchase_credit
    op.drop_constraint('purchase_batch_credit_fk_store', 'purchase_batch_credit', type_='foreignkey')
    op.drop_constraint('purchase_batch_credit_fk_vendor', 'purchase_batch_credit', type_='foreignkey')
    op.drop_constraint('purchase_batch_credit_fk_product', 'purchase_batch_credit', type_='foreignkey')
    op.drop_constraint('purchase_batch_credit_fk_mispick_product', 'purchase_batch_credit', type_='foreignkey')
    op.drop_constraint('purchase_batch_credit_fk_row', 'purchase_batch_credit', type_='foreignkey')
    op.rename_table('purchase_batch_credit', 'batch_purchase_credit')
    op.create_foreign_key('batch_purchase_credit_fk_store',
                          'batch_purchase_credit', 'store',
                          ['store_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_credit_fk_vendor',
                          'batch_purchase_credit', 'vendor',
                          ['vendor_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_credit_fk_product',
                          'batch_purchase_credit', 'product',
                          ['product_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_credit_fk_mispick_product',
                          'batch_purchase_credit', 'product',
                          ['mispick_product_uuid'], ['uuid'])
    op.create_foreign_key('batch_purchase_credit_fk_row',
                          'batch_purchase_credit', 'batch_purchase_row',
                          ['row_uuid'], ['uuid'])


def downgrade():

    # purchase
    op.drop_constraint('purchase_fk_buyer', 'purchase', type_='foreignkey')
    op.create_foreign_key('purchase_purchase_fk_buyer',
                          'purchase', 'employee',
                          ['buyer_uuid'], ['uuid'])

    # remove references to `batch_purchase`
    op.drop_constraint('batch_purchase_row_fk_batch_uuid', 'batch_purchase_row', type_='foreignkey')

    # batch_purchase
    op.drop_constraint('batch_purchase_fk_created_by', 'batch_purchase', type_='foreignkey')
    op.drop_constraint('batch_purchase_fk_cognized_by', 'batch_purchase', type_='foreignkey')
    op.drop_constraint('batch_purchase_fk_executed_by', 'batch_purchase', type_='foreignkey')
    op.drop_constraint('batch_purchase_fk_store', 'batch_purchase', type_='foreignkey')
    op.drop_constraint('batch_purchase_fk_vendor', 'batch_purchase', type_='foreignkey')
    op.drop_constraint('batch_purchase_fk_department', 'batch_purchase', type_='foreignkey')
    op.drop_constraint('batch_purchase_fk_buyer', 'batch_purchase', type_='foreignkey')
    op.drop_constraint('batch_purchase_fk_purchase', 'batch_purchase', type_='foreignkey')
    op.drop_constraint('batch_purchase_fk_truck_dump_batch', 'batch_purchase', type_='foreignkey')
    op.rename_table('batch_purchase', 'purchase_batch')
    op.create_foreign_key('purchase_batch_fk_created_by',
                          'purchase_batch', 'user',
                          ['created_by_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_fk_cognized_by',
                          'purchase_batch', 'user',
                          ['cognized_by_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_fk_executed_by',
                          'purchase_batch', 'user',
                          ['executed_by_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_fk_store',
                          'purchase_batch', 'store',
                          ['store_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_fk_vendor',
                          'purchase_batch', 'vendor',
                          ['vendor_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_fk_department',
                          'purchase_batch', 'department',
                          ['department_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_purchase_fk_buyer',
                          'purchase_batch', 'employee',
                          ['buyer_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_fk_purchase',
                          'purchase_batch', 'purchase',
                          ['purchase_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_fk_truck_dump_batch',
                          'purchase_batch', 'purchase_batch',
                          ['truck_dump_batch_uuid'], ['uuid'])

    # batch_purchase_row
    op.drop_constraint('batch_purchase_row_fk_product', 'batch_purchase_row', type_='foreignkey')
    op.drop_constraint('batch_purchase_row_fk_item', 'batch_purchase_row', type_='foreignkey')
    op.rename_table('batch_purchase_row', 'purchase_batch_row')
    op.create_foreign_key('purchase_batch_row_fk_batch_uuid',
                          'purchase_batch_row', 'purchase_batch',
                          ['batch_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_row_fk_product',
                          'purchase_batch_row', 'product',
                          ['product_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_row_fk_item',
                          'purchase_batch_row', 'purchase_item',
                          ['item_uuid'], ['uuid'])

    # batch_purchase_row_claim
    op.drop_constraint('batch_purchase_row_claim_fk_claiming_row', 'batch_purchase_row_claim', type_='foreignkey')
    op.drop_constraint('batch_purchase_row_claim_fk_claimed_row', 'batch_purchase_row_claim', type_='foreignkey')
    op.rename_table('batch_purchase_row_claim', 'purchase_batch_row_claim')
    op.create_foreign_key('purchase_batch_row_claim_fk_claiming_row',
                          'purchase_batch_row_claim', 'purchase_batch_row',
                          ['claiming_row_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_row_claim_fk_claimed_row',
                          'purchase_batch_row_claim', 'purchase_batch_row',
                          ['claimed_row_uuid'], ['uuid'])

    # batch_purchase_credit
    op.drop_constraint('batch_purchase_credit_fk_store', 'batch_purchase_credit', type_='foreignkey')
    op.drop_constraint('batch_purchase_credit_fk_vendor', 'batch_purchase_credit', type_='foreignkey')
    op.drop_constraint('batch_purchase_credit_fk_product', 'batch_purchase_credit', type_='foreignkey')
    op.drop_constraint('batch_purchase_credit_fk_mispick_product', 'batch_purchase_credit', type_='foreignkey')
    op.drop_constraint('batch_purchase_credit_fk_row', 'batch_purchase_credit', type_='foreignkey')
    op.rename_table('batch_purchase_credit', 'purchase_batch_credit')
    op.create_foreign_key('purchase_batch_credit_fk_store',
                          'purchase_batch_credit', 'store',
                          ['store_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_credit_fk_vendor',
                          'purchase_batch_credit', 'vendor',
                          ['vendor_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_credit_fk_product',
                          'purchase_batch_credit', 'product',
                          ['product_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_credit_fk_mispick_product',
                          'purchase_batch_credit', 'product',
                          ['mispick_product_uuid'], ['uuid'])
    op.create_foreign_key('purchase_batch_credit_fk_row',
                          'purchase_batch_credit', 'purchase_batch_row',
                          ['row_uuid'], ['uuid'])
