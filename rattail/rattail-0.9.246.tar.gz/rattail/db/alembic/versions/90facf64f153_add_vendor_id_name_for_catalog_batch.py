# -*- coding: utf-8; -*-
"""add vendor id, name for catalog batch

Revision ID: 90facf64f153
Revises: 387ba7573623
Create Date: 2021-02-14 12:04:17.321423

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '90facf64f153'
down_revision = '387ba7573623'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_vendorcatalog
    op.add_column('batch_vendorcatalog', sa.Column('vendor_id', sa.String(length=15), nullable=True))
    op.add_column('batch_vendorcatalog', sa.Column('vendor_name', sa.String(length=50), nullable=True))
    op.alter_column('batch_vendorcatalog', 'vendor_uuid',
               existing_type=sa.VARCHAR(length=32),
               nullable=True)


def downgrade():

    # batch_vendorcatalog
    # TODO: cannot necessarily reverse this one..?
    op.alter_column('batch_vendorcatalog', 'vendor_uuid',
               existing_type=sa.VARCHAR(length=32),
               nullable=False)
    op.drop_column('batch_vendorcatalog', 'vendor_name')
    op.drop_column('batch_vendorcatalog', 'vendor_id')
