# -*- coding: utf-8; -*-
"""rename batch_vendorinvoice

Revision ID: 117236288811
Revises: 89e2406859be
Create Date: 2021-02-02 13:36:28.621440

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '117236288811'
down_revision = '89e2406859be'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # remove references to `vendor_invoice`
    op.drop_constraint('vendor_invoice_row_fk_batch', 'vendor_invoice_row', type_='foreignkey')

    # batch_vendorinvoice
    op.drop_constraint('vendor_invoice_fk_created_by', 'vendor_invoice', type_='foreignkey')
    op.drop_constraint('vendor_invoice_fk_cognized_by', 'vendor_invoice', type_='foreignkey')
    op.drop_constraint('vendor_invoice_fk_executed_by', 'vendor_invoice', type_='foreignkey')
    op.drop_constraint('vendor_invoice_fk_vendor', 'vendor_invoice', type_='foreignkey')
    op.rename_table('vendor_invoice', 'batch_vendorinvoice')
    op.create_foreign_key('batch_vendorinvoice_fk_created_by',
                          'batch_vendorinvoice', 'user',
                          ['created_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_vendorinvoice_fk_cognized_by',
                          'batch_vendorinvoice', 'user',
                          ['cognized_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_vendorinvoice_fk_executed_by',
                          'batch_vendorinvoice', 'user',
                          ['executed_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_vendorinvoice_fk_vendor',
                          'batch_vendorinvoice', 'vendor',
                          ['vendor_uuid'], ['uuid'])

    # batch_vendorinvoice_row
    op.drop_constraint('vendor_invoice_row_fk_product', 'vendor_invoice_row', type_='foreignkey')
    op.rename_table('vendor_invoice_row', 'batch_vendorinvoice_row')
    op.create_foreign_key('batch_vendorinvoice_row_fk_batch_uuid',
                          'batch_vendorinvoice_row', 'batch_vendorinvoice',
                          ['batch_uuid'], ['uuid'])
    op.create_foreign_key('batch_vendorinvoice_row_fk_product',
                          'batch_vendorinvoice_row', 'product',
                          ['product_uuid'], ['uuid'])
    

def downgrade():

    # remove references to `batch_vendorinvoice`
    op.drop_constraint('batch_vendorinvoice_row_fk_batch_uuid', 'batch_vendorinvoice_row', type_='foreignkey')

    # batch_vendorinvoice
    op.drop_constraint('batch_vendorinvoice_fk_created_by', 'batch_vendorinvoice', type_='foreignkey')
    op.drop_constraint('batch_vendorinvoice_fk_cognized_by', 'batch_vendorinvoice', type_='foreignkey')
    op.drop_constraint('batch_vendorinvoice_fk_executed_by', 'batch_vendorinvoice', type_='foreignkey')
    op.drop_constraint('batch_vendorinvoice_fk_vendor', 'batch_vendorinvoice', type_='foreignkey')
    op.rename_table('batch_vendorinvoice', 'vendor_invoice')
    op.create_foreign_key('vendor_invoice_fk_created_by',
                          'vendor_invoice', 'user',
                          ['created_by_uuid'], ['uuid'])
    op.create_foreign_key('vendor_invoice_fk_cognized_by',
                          'vendor_invoice', 'user',
                          ['cognized_by_uuid'], ['uuid'])
    op.create_foreign_key('vendor_invoice_fk_executed_by',
                          'vendor_invoice', 'user',
                          ['executed_by_uuid'], ['uuid'])
    op.create_foreign_key('vendor_invoice_fk_vendor',
                          'vendor_invoice', 'vendor',
                          ['vendor_uuid'], ['uuid'])

    # batch_vendorinvoice_row
    op.drop_constraint('batch_vendorinvoice_row_fk_product', 'batch_vendorinvoice_row', type_='foreignkey')
    op.rename_table('batch_vendorinvoice_row', 'vendor_invoice_row')
    op.create_foreign_key('vendor_invoice_row_fk_batch',
                          'vendor_invoice_row', 'vendor_invoice',
                          ['batch_uuid'], ['uuid'])
    op.create_foreign_key('vendor_invoice_row_fk_product',
                          'vendor_invoice_row', 'product',
                          ['product_uuid'], ['uuid'])
