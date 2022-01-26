# -*- coding: utf-8; -*-
"""add batch.params

Revision ID: 5ff1dddc0a30
Revises: 4f026ae58751
Create Date: 2019-10-08 17:17:23.616763

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '5ff1dddc0a30'
down_revision = '4f026ae58751'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch*
    op.add_column('batch_handheld', sa.Column('params', rattail.db.types.JSONTextDict(), nullable=True))
    op.add_column('batch_importer', sa.Column('params', rattail.db.types.JSONTextDict(), nullable=True))
    op.add_column('batch_inventory', sa.Column('params', rattail.db.types.JSONTextDict(), nullable=True))
    op.add_column('batch_newproduct', sa.Column('params', rattail.db.types.JSONTextDict(), nullable=True))
    op.add_column('batch_pricing', sa.Column('params', rattail.db.types.JSONTextDict(), nullable=True))
    op.add_column('batch_product', sa.Column('params', rattail.db.types.JSONTextDict(), nullable=True))
    op.add_column('label_batch', sa.Column('params', rattail.db.types.JSONTextDict(), nullable=True))
    op.add_column('purchase_batch', sa.Column('params', rattail.db.types.JSONTextDict(), nullable=True))
    op.add_column('vendor_catalog', sa.Column('params', rattail.db.types.JSONTextDict(), nullable=True))
    op.add_column('vendor_invoice', sa.Column('params', rattail.db.types.JSONTextDict(), nullable=True))


def downgrade():

    # batch*
    op.drop_column('vendor_invoice', 'params')
    op.drop_column('vendor_catalog', 'params')
    op.drop_column('purchase_batch', 'params')
    op.drop_column('label_batch', 'params')
    op.drop_column('batch_product', 'params')
    op.drop_column('batch_pricing', 'params')
    op.drop_column('batch_newproduct', 'params')
    op.drop_column('batch_inventory', 'params')
    op.drop_column('batch_importer', 'params')
    op.drop_column('batch_handheld', 'params')
