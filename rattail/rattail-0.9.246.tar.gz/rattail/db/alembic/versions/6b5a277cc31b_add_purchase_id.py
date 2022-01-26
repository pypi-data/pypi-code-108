# -*- coding: utf-8; -*-
"""add purchase.id

Revision ID: 6b5a277cc31b
Revises: 2afee42cc24d
Create Date: 2021-01-29 12:44:46.663170

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '6b5a277cc31b'
down_revision = '2afee42cc24d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase
    op.add_column('purchase', sa.Column('id', sa.Integer(), nullable=True))


def downgrade():

    # purchase
    op.drop_column('purchase', 'id')
