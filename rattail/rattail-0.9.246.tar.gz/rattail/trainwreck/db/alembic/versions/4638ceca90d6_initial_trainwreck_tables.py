# -*- coding: utf-8; -*-
"""initial Trainwreck tables

Revision ID: 4638ceca90d6
Revises: 
Create Date: 2021-02-15 15:02:18.976439

"""

from __future__ import unicode_literals, absolute_import

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4638ceca90d6'
down_revision = None
branch_labels = ('trainwreck',)
depends_on = None


def upgrade():

    # transaction
    op.create_table('transaction',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('system', sa.String(length=50), nullable=True),
                    sa.Column('system_id', sa.String(length=50), nullable=True),
                    sa.Column('terminal_id', sa.String(length=20), nullable=True),
                    sa.Column('receipt_number', sa.String(length=20), nullable=True),
                    sa.Column('start_time', sa.DateTime(), nullable=True),
                    sa.Column('end_time', sa.DateTime(), nullable=True),
                    sa.Column('upload_time', sa.DateTime(), nullable=True),
                    sa.Column('cashier_id', sa.String(length=20), nullable=True),
                    sa.Column('cashier_name', sa.String(length=255), nullable=True),
                    sa.Column('customer_id', sa.String(length=20), nullable=True),
                    sa.Column('customer_name', sa.String(length=255), nullable=True),
                    sa.Column('shopper_id', sa.String(length=20), nullable=True),
                    sa.Column('shopper_name', sa.String(length=255), nullable=True),
                    sa.Column('subtotal', sa.Numeric(precision=9, scale=2), nullable=True),
                    sa.Column('discounted_subtotal', sa.Numeric(precision=9, scale=2), nullable=True),
                    sa.Column('tax', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax1', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax2', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax3', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax4', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax5', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax6', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax7', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('cashback', sa.Numeric(precision=9, scale=2), nullable=True),
                    sa.Column('total', sa.Numeric(precision=9, scale=2), nullable=True),
                    sa.Column('void', sa.Boolean(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index('transaction_ix_end_time', 'transaction', ['end_time'], unique=False)
    op.create_index('transaction_ix_receipt_number', 'transaction', ['receipt_number'], unique=False)
    op.create_index('transaction_ix_start_time', 'transaction', ['start_time'], unique=False)
    op.create_index('transaction_ix_upload_time', 'transaction', ['upload_time'], unique=False)

    # transaction_item
    op.create_table('transaction_item',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('transaction_uuid', sa.String(length=32), nullable=False),
                    sa.Column('sequence', sa.Integer(), nullable=False),
                    sa.Column('item_type', sa.String(length=50), nullable=True),
                    sa.Column('item_scancode', sa.String(length=20), nullable=False),
                    sa.Column('item_id', sa.String(length=50), nullable=True),
                    sa.Column('department_number', sa.Integer(), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('exempt_from_gross_sales', sa.Boolean(), nullable=True),
                    sa.Column('brand_name', sa.String(length=100), nullable=True),
                    sa.Column('description', sa.String(length=255), nullable=False),
                    sa.Column('unit_price', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('unit_regular_price', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('unit_discounted_price', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('unit_quantity', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('subtotal', sa.Numeric(precision=9, scale=2), nullable=True),
                    sa.Column('discounted_subtotal', sa.Numeric(precision=9, scale=2), nullable=True),
                    sa.Column('gross_sales', sa.Numeric(precision=9, scale=2), nullable=True),
                    sa.Column('net_sales', sa.Numeric(precision=9, scale=2), nullable=True),
                    sa.Column('tax', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax1', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax2', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax3', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax4', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax5', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax6', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('tax7', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('total', sa.Numeric(precision=9, scale=2), nullable=True),
                    sa.Column('void', sa.Boolean(), nullable=False),
                    sa.Column('error_correct', sa.Boolean(), nullable=False),
                    sa.ForeignKeyConstraint(['transaction_uuid'], ['transaction.uuid'], name='transaction_item_fk_transaction'),
                    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index('transaction_item_ix_item_id', 'transaction_item', ['item_id'], unique=False)
    op.create_index('transaction_item_ix_transaction_uuid', 'transaction_item', ['transaction_uuid'], unique=False)


def downgrade():

    # transaction_item
    op.drop_index('transaction_item_ix_transaction_uuid', table_name='transaction_item')
    op.drop_index('transaction_item_ix_item_id', table_name='transaction_item')
    op.drop_table('transaction_item')

    # transaction
    op.drop_index('transaction_ix_upload_time', table_name='transaction')
    op.drop_index('transaction_ix_start_time', table_name='transaction')
    op.drop_index('transaction_ix_receipt_number', table_name='transaction')
    op.drop_index('transaction_ix_end_time', table_name='transaction')
    op.drop_table('transaction')
