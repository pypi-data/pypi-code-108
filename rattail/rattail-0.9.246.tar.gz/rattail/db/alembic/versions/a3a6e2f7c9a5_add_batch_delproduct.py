# -*- coding: utf-8; -*-
"""add batch_delproduct

Revision ID: a3a6e2f7c9a5
Revises: ef398701ffc6
Create Date: 2021-01-15 17:34:41.926477

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'a3a6e2f7c9a5'
down_revision = 'ef398701ffc6'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_delproduct
    op.create_table('batch_delproduct',
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
                    sa.ForeignKeyConstraint(['cognized_by_uuid'], ['user.uuid'], name='batch_delproduct_fk_cognized_by'),
                    sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'], name='batch_delproduct_fk_created_by'),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], ['user.uuid'], name='batch_delproduct_fk_executed_by'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # batch_delproduct_row
    op.create_table('batch_delproduct_row',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('batch_uuid', sa.String(length=32), nullable=False),
                    sa.Column('sequence', sa.Integer(), nullable=False),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.Column('status_text', sa.String(length=255), nullable=True),
                    sa.Column('modified', sa.DateTime(), nullable=True),
                    sa.Column('removed', sa.Boolean(), nullable=False),
                    sa.Column('item_entry', sa.String(length=32), nullable=True),
                    sa.Column('upc', rattail.db.types.GPCType(), nullable=True),
                    sa.Column('item_id', sa.String(length=20), nullable=True),
                    sa.Column('product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('brand_name', sa.String(length=100), nullable=True),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('size', sa.String(length=255), nullable=True),
                    sa.Column('department_number', sa.Integer(), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('subdepartment_number', sa.Integer(), nullable=True),
                    sa.Column('subdepartment_name', sa.String(length=30), nullable=True),
                    sa.ForeignKeyConstraint(['batch_uuid'], ['batch_delproduct.uuid'], name='batch_delproduct_row_fk_batch'),
                    sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='batch_delproduct_row_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # batch_delproduct*
    op.drop_table('batch_delproduct_row')
    op.drop_table('batch_delproduct')
