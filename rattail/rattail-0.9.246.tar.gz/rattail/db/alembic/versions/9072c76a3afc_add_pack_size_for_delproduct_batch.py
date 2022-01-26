# -*- coding: utf-8; -*-
"""add pack_size for delproduct batch

Revision ID: 9072c76a3afc
Revises: b47eeb5fcf79
Create Date: 2021-07-15 12:40:18.374163

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '9072c76a3afc'
down_revision = 'b47eeb5fcf79'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_delproduct_row
    op.add_column('batch_delproduct_row', sa.Column('pack_size', sa.Numeric(precision=9, scale=4), nullable=True))


def downgrade():

    # batch_delproduct_row
    op.drop_column('batch_delproduct_row', 'pack_size')
