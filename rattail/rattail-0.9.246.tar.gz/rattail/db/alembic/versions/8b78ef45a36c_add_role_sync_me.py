# -*- coding: utf-8 -*-
"""add role.sync_me

Revision ID: 8b78ef45a36c
Revises: 675a0034becc
Create Date: 2021-10-13 18:00:46.665524

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '8b78ef45a36c'
down_revision = '675a0034becc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # role
    op.add_column('role', sa.Column('node_type', sa.String(length=100), nullable=True))
    op.add_column('role', sa.Column('sync_me', sa.Boolean(), nullable=True))
    op.add_column('role_version', sa.Column('node_type', sa.String(length=100), autoincrement=False, nullable=True))
    op.add_column('role_version', sa.Column('sync_me', sa.Boolean(), autoincrement=False, nullable=True))


def downgrade():

    # role
    op.drop_column('role_version', 'sync_me')
    op.drop_column('role_version', 'node_type')
    op.drop_column('role', 'sync_me')
    op.drop_column('role', 'node_type')
