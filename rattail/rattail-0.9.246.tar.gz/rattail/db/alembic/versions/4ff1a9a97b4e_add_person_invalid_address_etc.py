# -*- coding: utf-8; -*-
"""add Person.invalid_address etc.

Revision ID: 4ff1a9a97b4e
Revises: fd91ee24cead
Create Date: 2020-01-23 15:50:25.748439

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '4ff1a9a97b4e'
down_revision = u'fd91ee24cead'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # person
    op.add_column('person', sa.Column('invalid_address', sa.Boolean(), nullable=True))
    op.add_column('person_version', sa.Column('invalid_address', sa.Boolean(), autoincrement=False, nullable=True))

    # customer
    op.add_column('customer', sa.Column('invalid_address', sa.Boolean(), nullable=True))
    op.add_column('customer_version', sa.Column('invalid_address', sa.Boolean(), autoincrement=False, nullable=True))

    # member
    op.add_column('member', sa.Column('invalid_address', sa.Boolean(), nullable=True))
    op.add_column('member_version', sa.Column('invalid_address', sa.Boolean(), autoincrement=False, nullable=True))


def downgrade():

    # member
    op.drop_column('member_version', 'invalid_address')
    op.drop_column('member', 'invalid_address')

    # customer
    op.drop_column('customer_version', 'invalid_address')
    op.drop_column('customer', 'invalid_address')

    # person
    op.drop_column('person_version', 'invalid_address')
    op.drop_column('person', 'invalid_address')
