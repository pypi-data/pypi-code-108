# -*- coding: utf-8; -*-
"""add product.average_weight

Revision ID: c8981df473d0
Revises: efb7cd318947
Create Date: 2020-09-02 13:13:42.629959

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'c8981df473d0'
down_revision = u'efb7cd318947'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product
    op.add_column('product', sa.Column('average_weight', sa.Numeric(precision=12, scale=3), nullable=True))
    op.add_column('product_version', sa.Column('average_weight', sa.Numeric(precision=12, scale=3), autoincrement=False, nullable=True))


def downgrade():

    # product
    op.drop_column('product_version', 'average_weight')
    op.drop_column('product', 'average_weight')
