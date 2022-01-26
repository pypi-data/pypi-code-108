# -*- coding: utf-8; -*-
"""add tpr, current price for label batch

Revision ID: d8b0ba4fa795
Revises: 08cc2ef12c18
Create Date: 2022-01-10 13:46:56.056570

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'd8b0ba4fa795'
down_revision = '08cc2ef12c18'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_labels_row
    op.add_column('batch_labels_row', sa.Column('tpr_price', sa.Numeric(precision=8, scale=3), nullable=True))
    op.add_column('batch_labels_row', sa.Column('tpr_starts', sa.DateTime(), nullable=True))
    op.add_column('batch_labels_row', sa.Column('tpr_ends', sa.DateTime(), nullable=True))
    op.add_column('batch_labels_row', sa.Column('current_price', sa.Numeric(precision=8, scale=3), nullable=True))
    op.add_column('batch_labels_row', sa.Column('current_starts', sa.DateTime(), nullable=True))
    op.add_column('batch_labels_row', sa.Column('current_ends', sa.DateTime(), nullable=True))


def downgrade():

    # batch_labels_row
    op.drop_column('batch_labels_row', 'current_ends')
    op.drop_column('batch_labels_row', 'current_starts')
    op.drop_column('batch_labels_row', 'current_price')
    op.drop_column('batch_labels_row', 'tpr_ends')
    op.drop_column('batch_labels_row', 'tpr_starts')
    op.drop_column('batch_labels_row', 'tpr_price')
