# -*- coding: utf-8; -*-
"""rename batch_vendorcatalog

Revision ID: 89e2406859be
Revises: 6b5a277cc31b
Create Date: 2021-02-02 12:44:00.529051

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '89e2406859be'
down_revision = '6b5a277cc31b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # remove references to `vendor_catalog`
    op.drop_constraint('vendor_catalog_row_fk_batch_uuid', 'vendor_catalog_row', type_='foreignkey')

    # batch_vendorcatalog
    op.drop_constraint('vendor_catalog_fk_created_by', 'vendor_catalog', type_='foreignkey')
    op.drop_constraint('vendor_catalog_fk_cognized_by', 'vendor_catalog', type_='foreignkey')
    op.drop_constraint('vendor_catalog_fk_executed_by', 'vendor_catalog', type_='foreignkey')
    op.drop_constraint('vendor_catalog_fk_vendor', 'vendor_catalog', type_='foreignkey')
    op.rename_table('vendor_catalog', 'batch_vendorcatalog')
    op.create_foreign_key('batch_vendorcatalog_fk_created_by',
                          'batch_vendorcatalog', 'user',
                          ['created_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_vendorcatalog_fk_cognized_by',
                          'batch_vendorcatalog', 'user',
                          ['cognized_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_vendorcatalog_fk_executed_by',
                          'batch_vendorcatalog', 'user',
                          ['executed_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_vendorcatalog_fk_vendor',
                          'batch_vendorcatalog', 'vendor',
                          ['vendor_uuid'], ['uuid'])

    # batch_vendorcatalog_row
    op.drop_constraint('vendor_catalog_row_fk_product', 'vendor_catalog_row', type_='foreignkey')
    op.drop_constraint('vendor_catalog_row_fk_cost', 'vendor_catalog_row', type_='foreignkey')
    op.rename_table('vendor_catalog_row', 'batch_vendorcatalog_row')
    op.create_foreign_key('batch_vendorcatalog_row_fk_batch_uuid',
                          'batch_vendorcatalog_row', 'batch_vendorcatalog',
                          ['batch_uuid'], ['uuid'])
    op.create_foreign_key('batch_vendorcatalog_row_fk_product',
                          'batch_vendorcatalog_row', 'product',
                          ['product_uuid'], ['uuid'])
    op.create_foreign_key('batch_vendorcatalog_row_fk_cost',
                          'batch_vendorcatalog_row', 'product_cost',
                          ['cost_uuid'], ['uuid'])


def downgrade():

    # remove references to `batch_vendorcatalog`
    op.drop_constraint('batch_vendorcatalog_row_fk_batch_uuid', 'batch_vendorcatalog_row', type_='foreignkey')

    # batch_vendorcatalog
    op.drop_constraint('batch_vendorcatalog_fk_created_by', 'batch_vendorcatalog', type_='foreignkey')
    op.drop_constraint('batch_vendorcatalog_fk_cognized_by', 'batch_vendorcatalog', type_='foreignkey')
    op.drop_constraint('batch_vendorcatalog_fk_executed_by', 'batch_vendorcatalog', type_='foreignkey')
    op.drop_constraint('batch_vendorcatalog_fk_vendor', 'batch_vendorcatalog', type_='foreignkey')
    op.rename_table('batch_vendorcatalog', 'vendor_catalog')
    op.create_foreign_key('vendor_catalog_fk_created_by',
                          'vendor_catalog', 'user',
                          ['created_by_uuid'], ['uuid'])
    op.create_foreign_key('vendor_catalog_fk_cognized_by',
                          'vendor_catalog', 'user',
                          ['cognized_by_uuid'], ['uuid'])
    op.create_foreign_key('vendor_catalog_fk_executed_by',
                          'vendor_catalog', 'user',
                          ['executed_by_uuid'], ['uuid'])
    op.create_foreign_key('vendor_catalog_fk_vendor',
                          'vendor_catalog', 'vendor',
                          ['vendor_uuid'], ['uuid'])

    # batch_vendorcatalog_row
    op.drop_constraint('batch_vendorcatalog_row_fk_product', 'batch_vendorcatalog_row', type_='foreignkey')
    op.drop_constraint('batch_vendorcatalog_row_fk_cost', 'batch_vendorcatalog_row', type_='foreignkey')
    op.rename_table('batch_vendorcatalog_row', 'vendor_catalog_row')
    op.create_foreign_key('vendor_catalog_row_fk_batch_uuid',
                          'vendor_catalog_row', 'vendor_catalog',
                          ['batch_uuid'], ['uuid'])
    op.create_foreign_key('vendor_catalog_row_fk_product',
                          'vendor_catalog_row', 'product',
                          ['product_uuid'], ['uuid'])
    op.create_foreign_key('vendor_catalog_row_fk_cost',
                          'vendor_catalog_row', 'product_cost',
                          ['cost_uuid'], ['uuid'])
