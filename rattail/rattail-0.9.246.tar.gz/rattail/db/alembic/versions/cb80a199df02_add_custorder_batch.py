# -*- coding: utf-8; -*-
"""add custorder_batch

Revision ID: cb80a199df02
Revises: aeea3c6fc6af
Create Date: 2020-08-02 01:15:56.242415

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'cb80a199df02'
down_revision = 'aeea3c6fc6af'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # custorder
    op.add_column('custorder', sa.Column('email_address', sa.String(length=255), nullable=True))
    op.add_column('custorder', sa.Column('phone_number', sa.String(length=20), nullable=True))
    op.add_column('custorder', sa.Column('created_by_uuid', sa.String(length=32), nullable=True))
    op.add_column('custorder', sa.Column('store_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key('custorder_fk_created_by', 'custorder', 'user', ['created_by_uuid'], ['uuid'])
    op.create_foreign_key('custorder_fk_store', 'custorder', 'store', ['store_uuid'], ['uuid'])

    # custorder_batch
    op.create_table('custorder_batch',
                    sa.Column('store_uuid', sa.String(length=32), nullable=True),
                    sa.Column('customer_uuid', sa.String(length=32), nullable=True),
                    sa.Column('person_uuid', sa.String(length=32), nullable=True),
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('cognized', sa.DateTime(), nullable=True),
                    sa.Column('cognized_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('rowcount', sa.Integer(), nullable=True),
                    sa.Column('complete', sa.Boolean(), nullable=False),
                    sa.Column('executed', sa.DateTime(), nullable=True),
                    sa.Column('executed_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('purge', sa.Date(), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.Column('params', rattail.db.types.JSONTextDict(), nullable=True),
                    sa.Column('extra_data', sa.Text(), nullable=True),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.Column('status_text', sa.String(length=255), nullable=True),
                    sa.Column('order_uuid', sa.String(length=32), nullable=True),
                    sa.Column('mode', sa.Integer(), nullable=False),
                    sa.Column('email_address', sa.String(length=255), nullable=True),
                    sa.Column('phone_number', sa.String(length=20), nullable=True),
                    sa.ForeignKeyConstraint(['cognized_by_uuid'], ['user.uuid'], name='custorder_batch_fk_cognized_by'),
                    sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'], name='custorder_batch_fk_created_by'),
                    sa.ForeignKeyConstraint(['customer_uuid'], ['customer.uuid'], name='custorder_batch_fk_customer'),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], ['user.uuid'], name='custorder_batch_fk_executed_by'),
                    sa.ForeignKeyConstraint(['order_uuid'], ['custorder.uuid'], name='custorder_batch_fk_order'),
                    sa.ForeignKeyConstraint(['person_uuid'], ['person.uuid'], name='custorder_batch_fk_person'),
                    sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'], name='custorder_batch_fk_store'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # custorder_batch_row
    op.create_table('custorder_batch_row',
                    sa.Column('product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('product_brand', sa.String(length=100), nullable=True),
                    sa.Column('product_description', sa.String(length=60), nullable=True),
                    sa.Column('product_size', sa.String(length=30), nullable=True),
                    sa.Column('product_unit_of_measure', sa.String(length=4), nullable=False),
                    sa.Column('department_number', sa.Integer(), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('case_quantity', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('cases_ordered', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('units_ordered', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('product_unit_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('unit_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('discount_percent', sa.Numeric(precision=5, scale=3), nullable=False),
                    sa.Column('total_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('paid_amount', sa.Numeric(precision=8, scale=3), nullable=False),
                    sa.Column('payment_transaction_number', sa.String(length=8), nullable=True),
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('batch_uuid', sa.String(length=32), nullable=False),
                    sa.Column('sequence', sa.Integer(), nullable=False),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.Column('status_text', sa.String(length=255), nullable=True),
                    sa.Column('modified', sa.DateTime(), nullable=True),
                    sa.Column('removed', sa.Boolean(), nullable=False),
                    sa.Column('item_entry', sa.String(length=32), nullable=True),
                    sa.Column('item_uuid', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['batch_uuid'], ['custorder_batch.uuid'], name='custorder_batch_row_fk_batch_uuid'),
                    sa.ForeignKeyConstraint(['item_uuid'], ['custorder_item.uuid'], name='custorder_batch_row_fk_item'),
                    sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='custorder_batch_row_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # custorder_batch*
    op.drop_table('custorder_batch_row')
    op.drop_table('custorder_batch')

    # custorder
    op.drop_constraint('custorder_fk_store', 'custorder', type_='foreignkey')
    op.drop_constraint('custorder_fk_created_by', 'custorder', type_='foreignkey')
    op.drop_column('custorder', 'store_uuid')
    op.drop_column('custorder', 'created_by_uuid')
    op.drop_column('custorder', 'phone_number')
    op.drop_column('custorder', 'email_address')
