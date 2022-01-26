# -*- coding: utf-8; -*-
"""add vendor catalog unit cost diff

Revision ID: 40c0c107ee6d
Revises: 5ff1dddc0a30
Create Date: 2019-10-09 13:50:57.673800

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '40c0c107ee6d'
down_revision = '5ff1dddc0a30'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # vendor_catalog_row
    op.add_column('vendor_catalog_row', sa.Column('unit_cost_diff_percent', sa.Numeric(precision=10, scale=5), nullable=True))


def downgrade():

    # vendor_catalog_row
    op.drop_column('vendor_catalog_row', 'unit_cost_diff_percent')
