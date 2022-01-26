# -*- coding: utf-8; -*-
"""grow permission name

Revision ID: efb7cd318947
Revises: 8adbe48ede2c
Create Date: 2020-08-10 19:33:53.406026

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'efb7cd318947'
down_revision = u'8adbe48ede2c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # permission
    op.alter_column('permission', 'permission', type_=sa.String(length=254))


def downgrade():

    # permission
    op.alter_column('permission', 'permission', type_=sa.String(length=50))
