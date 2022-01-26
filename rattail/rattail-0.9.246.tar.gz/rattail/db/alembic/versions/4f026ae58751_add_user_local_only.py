# -*- coding: utf-8; -*-
"""add user.local_only

Revision ID: 4f026ae58751
Revises: 64d163d9de3a
Create Date: 2019-10-04 19:00:05.519055

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '4f026ae58751'
down_revision = '64d163d9de3a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # person
    op.add_column('person', sa.Column('local_only', sa.Boolean(), nullable=True))
    op.add_column('person_version', sa.Column('local_only', sa.Boolean(), autoincrement=False, nullable=True))

    # user
    op.add_column('user', sa.Column('local_only', sa.Boolean(), nullable=True))
    op.add_column('user_version', sa.Column('local_only', sa.Boolean(), autoincrement=False, nullable=True))


def downgrade():

    # user
    op.drop_column('user_version', 'local_only')
    op.drop_column('user', 'local_only')

    # person
    op.drop_column('person_version', 'local_only')
    op.drop_column('person', 'local_only')
