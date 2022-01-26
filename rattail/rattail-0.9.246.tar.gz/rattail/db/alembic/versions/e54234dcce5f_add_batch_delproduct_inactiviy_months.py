# -*- coding: utf-8; -*-
"""add batch_delproduct.inactiviy_months

Revision ID: e54234dcce5f
Revises: 0e37a0b5dc9a
Create Date: 2021-03-09 11:35:30.446866

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'e54234dcce5f'
down_revision = '0e37a0b5dc9a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_delproduct
    op.add_column('batch_delproduct', sa.Column('inactivity_months', sa.Integer(), nullable=True))


def downgrade():

    # batch_delproduct
    op.drop_column('batch_delproduct', 'inactivity_months')
