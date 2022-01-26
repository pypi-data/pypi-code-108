# -*- coding: utf-8; -*-
"""add store.archived

Revision ID: b47eeb5fcf79
Revises: e54234dcce5f
Create Date: 2021-03-19 10:27:04.755507

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'b47eeb5fcf79'
down_revision = 'e54234dcce5f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # store
    op.add_column('store', sa.Column('archived', sa.Boolean(), nullable=True))
    op.add_column('store_version', sa.Column('archived', sa.Boolean(), autoincrement=False, nullable=True))


def downgrade():

    # store
    op.drop_column('store_version', 'archived')
    op.drop_column('store', 'archived')
