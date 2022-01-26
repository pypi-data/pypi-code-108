# -*- coding: utf-8; -*-
"""add Product.sale_price, tpr_price

Revision ID: 7d0c93d3ff1e
Revises: c45017b36f25
Create Date: 2020-01-03 17:59:04.746965

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '7d0c93d3ff1e'
down_revision = 'c45017b36f25'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product
    op.add_column('product', sa.Column('sale_price_uuid', sa.String(length=32), nullable=True))
    op.add_column('product', sa.Column('tpr_price_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key('product_fk_sale_price', 'product', 'product_price', ['sale_price_uuid'], ['uuid'], use_alter=True)
    op.create_foreign_key('product_fk_tpr_price', 'product', 'product_price', ['tpr_price_uuid'], ['uuid'], use_alter=True)
    op.add_column('product_version', sa.Column('sale_price_uuid', sa.String(length=32), autoincrement=False, nullable=True))
    op.add_column('product_version', sa.Column('tpr_price_uuid', sa.String(length=32), autoincrement=False, nullable=True))


def downgrade():

    # product
    op.drop_column('product_version', 'tpr_price_uuid')
    op.drop_column('product_version', 'sale_price_uuid')
    op.drop_constraint('product_fk_tpr_price', 'product', type_='foreignkey')
    op.drop_constraint('product_fk_sale_price', 'product', type_='foreignkey')
    op.drop_column('product', 'tpr_price_uuid')
    op.drop_column('product', 'sale_price_uuid')
