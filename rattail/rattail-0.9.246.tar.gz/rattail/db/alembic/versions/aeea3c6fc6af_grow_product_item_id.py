# -*- coding: utf-8; -*-
"""grow product.item_id

Revision ID: aeea3c6fc6af
Revises: 43d766defb6a
Create Date: 2020-06-29 15:18:17.898191

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'aeea3c6fc6af'
down_revision = u'43d766defb6a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product
    op.alter_column('product', 'item_id', type_=sa.String(length=50))
    op.alter_column('product_version', 'item_id', type_=sa.String(length=50))


def downgrade():

    # product
    op.alter_column('product_version', 'item_id', type_=sa.String(length=20))
    op.alter_column('product', 'item_id', type_=sa.String(length=20))
