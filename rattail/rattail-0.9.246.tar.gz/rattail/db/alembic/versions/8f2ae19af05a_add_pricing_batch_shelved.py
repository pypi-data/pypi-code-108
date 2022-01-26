# -*- coding: utf-8; -*-
"""add pricing_batch.shelved

Revision ID: 8f2ae19af05a
Revises: 6bbcd107cb35
Create Date: 2020-05-18 14:38:17.270416

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '8f2ae19af05a'
down_revision = '6bbcd107cb35'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_pricing
    op.add_column('batch_pricing', sa.Column('shelved', sa.Boolean(), nullable=True))
    batch = sa.sql.table('batch_pricing', sa.sql.column('shelved'))
    op.execute(batch.update().values({'shelved': False}))
    op.alter_column('batch_pricing', 'shelved', nullable=False,
                    existing_type=sa.Boolean())


def downgrade():

    # batch_pricing
    op.drop_column('batch_pricing', 'shelved')
