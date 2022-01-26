# -*- coding: utf-8; -*-
"""add pricing_batch_row.old_true_margin

Revision ID: 8adbe48ede2c
Revises: cb80a199df02
Create Date: 2020-08-09 15:41:46.923996

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '8adbe48ede2c'
down_revision = 'cb80a199df02'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_pricing_row
    op.add_column('batch_pricing_row', sa.Column('old_true_margin', sa.Numeric(precision=8, scale=3), nullable=True))


def downgrade():

    # batch_pricing_row
    op.drop_column('batch_pricing_row', 'old_true_margin')
