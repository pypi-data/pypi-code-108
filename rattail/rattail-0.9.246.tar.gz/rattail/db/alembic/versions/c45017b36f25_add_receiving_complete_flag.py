# -*- coding: utf-8; -*-
"""add receiving_complete flag

Revision ID: c45017b36f25
Revises: fd0975329091
Create Date: 2019-11-26 13:39:30.080843

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'c45017b36f25'
down_revision = 'fd0975329091'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch
    op.add_column('purchase_batch', sa.Column('receiving_complete', sa.Boolean(), nullable=True))


def downgrade():

    # purchase_batch
    op.drop_column('purchase_batch', 'receiving_complete')
