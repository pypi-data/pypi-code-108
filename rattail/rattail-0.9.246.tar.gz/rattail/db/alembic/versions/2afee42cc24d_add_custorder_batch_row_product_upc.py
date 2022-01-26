# -*- coding: utf-8; -*-
"""add custorder_batch_row.product_upc

Revision ID: 2afee42cc24d
Revises: a7b286e87f89
Create Date: 2021-01-25 21:32:00.008209

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '2afee42cc24d'
down_revision = 'a7b286e87f89'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # custorder
    op.add_column('custorder', sa.Column('total_price', sa.Numeric(precision=10, scale=3), nullable=True))

    # custorder_item
    op.alter_column('custorder_item', 'product_unit_of_measure',
               existing_type=sa.VARCHAR(length=4),
               nullable=True)
    op.add_column('custorder_item', sa.Column('product_upc', rattail.db.types.GPCType(), nullable=True))
    op.add_column('custorder_item', sa.Column('product_weighed', sa.Boolean(), nullable=True))
    op.add_column('custorder_item', sa.Column('order_quantity', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('custorder_item', sa.Column('order_uom', sa.String(length=4), nullable=True))

    # custorder_batch
    op.add_column('custorder_batch', sa.Column('total_price', sa.Numeric(precision=10, scale=3), nullable=True))

    # custorder_batch_row
    op.alter_column('custorder_batch_row', 'product_unit_of_measure',
               existing_type=sa.VARCHAR(length=4),
               nullable=True)
    op.add_column('custorder_batch_row', sa.Column('product_upc', rattail.db.types.GPCType(), nullable=True))
    op.add_column('custorder_batch_row', sa.Column('product_weighed', sa.Boolean(), nullable=True))
    op.add_column('custorder_batch_row', sa.Column('order_quantity', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('custorder_batch_row', sa.Column('order_uom', sa.String(length=4), nullable=True))


def downgrade():

    # custorder_batch_row
    op.drop_column('custorder_batch_row', 'order_uom')
    op.drop_column('custorder_batch_row', 'order_quantity')
    op.drop_column('custorder_batch_row', 'product_weighed')
    op.drop_column('custorder_batch_row', 'product_upc')
    # TODO: this is really a one-way change, cannot be easily undone
    # op.alter_column('custorder_batch_row', 'product_unit_of_measure',
    #            existing_type=sa.VARCHAR(length=4),
    #            nullable=False)

    # custorder_batch
    op.drop_column('custorder_batch', 'total_price')

    # custorder_item
    op.drop_column('custorder_item', 'order_uom')
    op.drop_column('custorder_item', 'order_quantity')
    op.drop_column('custorder_item', 'product_weighed')
    op.drop_column('custorder_item', 'product_upc')
    # TODO: this is really a one-way change, cannot be easily undone
    # op.alter_column('custorder_item', 'product_unit_of_measure',
    #            existing_type=sa.VARCHAR(length=4),
    #            nullable=False)

    # custorder
    op.drop_column('custorder', 'total_price')
