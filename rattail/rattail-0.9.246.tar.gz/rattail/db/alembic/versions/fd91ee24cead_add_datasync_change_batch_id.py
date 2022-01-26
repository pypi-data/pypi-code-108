# -*- coding: utf-8; -*-
"""add datasync_change.batch_id

Revision ID: fd91ee24cead
Revises: 7d0c93d3ff1e
Create Date: 2020-01-15 17:34:22.597552

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'fd91ee24cead'
down_revision = '7d0c93d3ff1e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types


batch_id_seq = sa.Sequence('datasync_change_batch_id_seq')


def upgrade():
    from sqlalchemy.schema import CreateSequence

    # datasync_change
    op.add_column('datasync_change', sa.Column('batch_id', sa.Integer(), nullable=True))
    op.add_column('datasync_change', sa.Column('batch_sequence', sa.Integer(), nullable=True))
    op.execute(CreateSequence(batch_id_seq))


def downgrade():
    from sqlalchemy.schema import DropSequence

    # datasync_change
    op.drop_column('datasync_change', 'batch_sequence')
    op.drop_column('datasync_change', 'batch_id')
    op.execute(DropSequence(batch_id_seq))
