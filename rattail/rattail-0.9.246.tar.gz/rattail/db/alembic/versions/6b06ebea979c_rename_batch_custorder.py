# -*- coding: utf-8; -*-
"""rename batch_custorder

Revision ID: 6b06ebea979c
Revises: 6a691bede834
Create Date: 2021-02-02 14:51:10.864672

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '6b06ebea979c'
down_revision = '6a691bede834'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # remove references to `custorder_batch`
    op.drop_constraint('custorder_batch_row_fk_batch_uuid', 'custorder_batch_row', type_='foreignkey')

    # batch_custorder
    op.drop_constraint('custorder_batch_fk_created_by', 'custorder_batch', type_='foreignkey')
    op.drop_constraint('custorder_batch_fk_cognized_by', 'custorder_batch', type_='foreignkey')
    op.drop_constraint('custorder_batch_fk_executed_by', 'custorder_batch', type_='foreignkey')
    op.drop_constraint('custorder_batch_fk_store', 'custorder_batch', type_='foreignkey')
    op.drop_constraint('custorder_batch_fk_customer', 'custorder_batch', type_='foreignkey')
    op.drop_constraint('custorder_batch_fk_person', 'custorder_batch', type_='foreignkey')
    op.drop_constraint('custorder_batch_fk_order', 'custorder_batch', type_='foreignkey')
    op.rename_table('custorder_batch', 'batch_custorder')
    op.create_foreign_key('batch_custorder_fk_created_by',
                          'batch_custorder', 'user',
                          ['created_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_custorder_fk_cognized_by',
                          'batch_custorder', 'user',
                          ['cognized_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_custorder_fk_executed_by',
                          'batch_custorder', 'user',
                          ['executed_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_custorder_fk_store',
                          'batch_custorder', 'store',
                          ['store_uuid'], ['uuid'])
    op.create_foreign_key('batch_custorder_fk_customer',
                          'batch_custorder', 'customer',
                          ['customer_uuid'], ['uuid'])
    op.create_foreign_key('batch_custorder_fk_person',
                          'batch_custorder', 'person',
                          ['person_uuid'], ['uuid'])
    op.create_foreign_key('batch_custorder_fk_order',
                          'batch_custorder', 'custorder',
                          ['order_uuid'], ['uuid'])

    # batch_custorder_row
    op.drop_constraint('custorder_batch_row_fk_product', 'custorder_batch_row', type_='foreignkey')
    op.drop_constraint('custorder_batch_row_fk_item', 'custorder_batch_row', type_='foreignkey')
    op.rename_table('custorder_batch_row', 'batch_custorder_row')
    op.create_foreign_key('batch_custorder_row_fk_batch_uuid',
                          'batch_custorder_row', 'batch_custorder',
                          ['batch_uuid'], ['uuid'])
    op.create_foreign_key('batch_custorder_row_fk_product',
                          'batch_custorder_row', 'product',
                          ['product_uuid'], ['uuid'])
    op.create_foreign_key('batch_custorder_row_fk_item',
                          'batch_custorder_row', 'custorder_item',
                          ['item_uuid'], ['uuid'])

def downgrade():

    # remove references to `batch_custorder`
    op.drop_constraint('batch_custorder_row_fk_batch_uuid', 'batch_custorder_row', type_='foreignkey')

    # batch_custorder
    op.drop_constraint('batch_custorder_fk_created_by', 'batch_custorder', type_='foreignkey')
    op.drop_constraint('batch_custorder_fk_cognized_by', 'batch_custorder', type_='foreignkey')
    op.drop_constraint('batch_custorder_fk_executed_by', 'batch_custorder', type_='foreignkey')
    op.drop_constraint('batch_custorder_fk_store', 'batch_custorder', type_='foreignkey')
    op.drop_constraint('batch_custorder_fk_customer', 'batch_custorder', type_='foreignkey')
    op.drop_constraint('batch_custorder_fk_person', 'batch_custorder', type_='foreignkey')
    op.drop_constraint('batch_custorder_fk_order', 'batch_custorder', type_='foreignkey')
    op.rename_table('batch_custorder', 'custorder_batch')
    op.create_foreign_key('custorder_batch_fk_created_by',
                          'custorder_batch', 'user',
                          ['created_by_uuid'], ['uuid'])
    op.create_foreign_key('custorder_batch_fk_cognized_by',
                          'custorder_batch', 'user',
                          ['cognized_by_uuid'], ['uuid'])
    op.create_foreign_key('custorder_batch_fk_executed_by',
                          'custorder_batch', 'user',
                          ['executed_by_uuid'], ['uuid'])
    op.create_foreign_key('custorder_batch_fk_store',
                          'custorder_batch', 'store',
                          ['store_uuid'], ['uuid'])
    op.create_foreign_key('custorder_batch_fk_customer',
                          'custorder_batch', 'customer',
                          ['customer_uuid'], ['uuid'])
    op.create_foreign_key('custorder_batch_fk_person',
                          'custorder_batch', 'person',
                          ['person_uuid'], ['uuid'])
    op.create_foreign_key('custorder_batch_fk_order',
                          'custorder_batch', 'custorder',
                          ['order_uuid'], ['uuid'])

    # batch_custorder_row
    op.drop_constraint('batch_custorder_row_fk_product', 'batch_custorder_row', type_='foreignkey')
    op.drop_constraint('batch_custorder_row_fk_item', 'batch_custorder_row', type_='foreignkey')
    op.rename_table('batch_custorder_row', 'custorder_batch_row')
    op.create_foreign_key('custorder_batch_row_fk_batch_uuid',
                          'custorder_batch_row', 'custorder_batch',
                          ['batch_uuid'], ['uuid'])
    op.create_foreign_key('custorder_batch_row_fk_product',
                          'custorder_batch_row', 'product',
                          ['product_uuid'], ['uuid'])
    op.create_foreign_key('custorder_batch_row_fk_item',
                          'custorder_batch_row', 'custorder_item',
                          ['item_uuid'], ['uuid'])
