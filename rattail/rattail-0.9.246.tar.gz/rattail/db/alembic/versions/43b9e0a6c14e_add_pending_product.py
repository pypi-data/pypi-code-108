# -*- coding: utf-8; -*-
"""add pending_product

Revision ID: 43b9e0a6c14e
Revises: 8856f697902d
Create Date: 2021-11-09 18:08:48.252950

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '43b9e0a6c14e'
down_revision = '8856f697902d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # pending_product
    op.create_table('pending_product',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('user_uuid', sa.String(length=32), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('upc', rattail.db.types.GPCType(), nullable=True),
                    sa.Column('scancode', sa.String(length=14), nullable=True),
                    sa.Column('item_id', sa.String(length=50), nullable=True),
                    sa.Column('item_type', sa.Integer(), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('department_uuid', sa.String(length=32), nullable=True),
                    sa.Column('brand_name', sa.String(length=100), nullable=True),
                    sa.Column('brand_uuid', sa.String(length=32), nullable=True),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('size', sa.String(length=30), nullable=True),
                    sa.Column('case_size', sa.Numeric(precision=9, scale=4), nullable=True),
                    sa.Column('regular_price_amount', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('special_order', sa.Boolean(), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['brand_uuid'], ['brand.uuid'], name='pending_product_fk_brand'),
                    sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'], name='pending_product_fk_department'),
                    sa.ForeignKeyConstraint(['user_uuid'], ['user.uuid'], name='pending_product_fk_user'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # pending_product
    op.drop_table('pending_product')
