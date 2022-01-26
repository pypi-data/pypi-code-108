# -*- coding: utf-8; -*-
"""add vendor invoice cost diff

Revision ID: 3ed719791439
Revises: 8e8c71d67fb8
Create Date: 2019-10-09 15:40:50.667401

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '3ed719791439'
down_revision = '8e8c71d67fb8'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # vendor_invoice_row
    op.add_column('vendor_invoice_row', sa.Column('unit_cost_diff', sa.Numeric(precision=9, scale=5), nullable=True))


def downgrade():

    # vendor_invoice_row
    op.drop_column('vendor_invoice_row', 'unit_cost_diff')
