# -*- coding: utf-8; -*-
"""add some indexes

Revision ID: 43d766defb6a
Revises: 8f2ae19af05a
Create Date: 2020-05-28 12:06:04.917389

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '43d766defb6a'
down_revision = u'8f2ae19af05a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # address
    op.create_index('address_ix_parent', 'address', ['parent_type', 'parent_uuid'], unique=False)

    # email
    op.create_index('email_ix_parent', 'email', ['parent_type', 'parent_uuid'], unique=False)

    # note
    op.create_index('note_ix_parent', 'note', ['parent_type', 'parent_uuid'], unique=False)

    # phone
    op.create_index('phone_ix_parent', 'phone', ['parent_type', 'parent_uuid'], unique=False)

    # user
    op.create_index('user_ix_person', 'user', ['person_uuid'], unique=False)

    # customer_x_person
    op.create_index('customer_x_person_ix_customer', 'customer_x_person', ['customer_uuid'], unique=False)
    op.create_index('customer_x_person_ix_person', 'customer_x_person', ['person_uuid'], unique=False)


def downgrade():

    # customer_x_person
    op.drop_index('customer_x_person_ix_person', table_name='customer_x_person')
    op.drop_index('customer_x_person_ix_customer', table_name='customer_x_person')

    # user
    op.drop_index('user_ix_person', table_name='user')

    # phone
    op.drop_index('phone_ix_parent', table_name='phone')

    # note
    op.drop_index('note_ix_parent', table_name='note')

    # email
    op.drop_index('email_ix_parent', table_name='email')

    # address
    op.drop_index('address_ix_parent', table_name='address')
