# -*- coding: utf-8; -*-
"""add batch_delproduct_row.present_in_scale

Revision ID: 387ba7573623
Revises: 82d3c2d9830d
Create Date: 2021-02-12 17:23:29.947961

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '387ba7573623'
down_revision = '82d3c2d9830d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # department
    op.add_column('department', sa.Column('allow_product_deletions', sa.Boolean(), nullable=True))
    op.add_column('department_version', sa.Column('allow_product_deletions', sa.Boolean(), autoincrement=False, nullable=True))

    # batch_delproduct_row
    op.add_column('batch_delproduct_row', sa.Column('present_in_scale', sa.Boolean(), nullable=True))


def downgrade():

    # batch_delproduct_row
    op.drop_column('batch_delproduct_row', 'present_in_scale')

    # department
    op.drop_column('department_version', 'allow_product_deletions')
    op.drop_column('department', 'allow_product_deletions')
