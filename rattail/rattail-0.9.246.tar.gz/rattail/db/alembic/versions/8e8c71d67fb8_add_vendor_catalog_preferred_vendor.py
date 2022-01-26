# -*- coding: utf-8; -*-
"""add vendor catalog preferred vendor

Revision ID: 8e8c71d67fb8
Revises: 40c0c107ee6d
Create Date: 2019-10-09 14:43:06.860218

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '8e8c71d67fb8'
down_revision = '40c0c107ee6d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # vendor_catalog_row
    op.add_column('vendor_catalog_row', sa.Column('is_preferred_vendor', sa.Boolean(), nullable=True))
    op.add_column('vendor_catalog_row', sa.Column('make_preferred_vendor', sa.Boolean(), nullable=True))


def downgrade():

    # vendor_catalog_row
    op.drop_column('vendor_catalog_row', 'make_preferred_vendor')
    op.drop_column('vendor_catalog_row', 'is_preferred_vendor')
