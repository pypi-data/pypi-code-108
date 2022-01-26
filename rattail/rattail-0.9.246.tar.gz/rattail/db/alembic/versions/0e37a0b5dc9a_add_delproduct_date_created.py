# -*- coding: utf-8; -*-
"""add delproduct.date_created

Revision ID: 0e37a0b5dc9a
Revises: 90facf64f153
Create Date: 2021-03-05 12:38:01.833618

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '0e37a0b5dc9a'
down_revision = '90facf64f153'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_delproduct_row
    op.add_column('batch_delproduct_row', sa.Column('date_created', sa.Date(), nullable=True))


def downgrade():

    # batch_delproduct_row
    op.drop_column('batch_delproduct_row', 'date_created')
