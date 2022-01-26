# -*- coding: utf-8; -*-
"""add Role.notes

Revision ID: 6bbcd107cb35
Revises: be2cb8322066
Create Date: 2020-03-23 19:36:16.940525

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '6bbcd107cb35'
down_revision = 'be2cb8322066'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # role
    op.add_column('role', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('role_version', sa.Column('notes', sa.Text(), autoincrement=False, nullable=True))


def downgrade():

    # role
    op.drop_column('role_version', 'notes')
    op.drop_column('role', 'notes')
