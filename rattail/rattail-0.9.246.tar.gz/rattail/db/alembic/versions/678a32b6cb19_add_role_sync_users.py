# -*- coding: utf-8; -*-
"""add role.sync_users

Revision ID: 678a32b6cb19
Revises: 43b9e0a6c14e
Create Date: 2021-11-13 14:52:37.243794

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '678a32b6cb19'
down_revision = '43b9e0a6c14e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # role
    op.add_column('role', sa.Column('sync_users', sa.Boolean(), nullable=True))
    op.add_column('role_version', sa.Column('sync_users', sa.Boolean(), autoincrement=False, nullable=True))


def downgrade():

    # role
    op.drop_column('role_version', 'sync_users')
    op.drop_column('role', 'sync_users')
