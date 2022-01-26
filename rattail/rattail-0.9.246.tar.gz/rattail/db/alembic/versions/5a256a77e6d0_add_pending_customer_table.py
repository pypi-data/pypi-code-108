# -*- coding: utf-8; -*-
"""add pending_customer table

Revision ID: 5a256a77e6d0
Revises: 51f7773bb07a
Create Date: 2021-10-06 16:35:39.749555

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '5a256a77e6d0'
down_revision = u'51f7773bb07a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # pending_customer
    op.create_table('pending_customer',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('user_uuid', sa.String(length=32), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('id', sa.String(length=20), nullable=True),
                    sa.Column('first_name', sa.String(length=50), nullable=True),
                    sa.Column('middle_name', sa.String(length=50), nullable=True),
                    sa.Column('last_name', sa.String(length=50), nullable=True),
                    sa.Column('display_name', sa.String(length=100), nullable=True),
                    sa.Column('phone_number', sa.String(length=20), nullable=True),
                    sa.Column('phone_type', sa.String(length=15), nullable=True),
                    sa.Column('email_address', sa.String(length=255), nullable=True),
                    sa.Column('email_type', sa.String(length=15), nullable=True),
                    sa.Column('address_street', sa.String(length=100), nullable=True),
                    sa.Column('address_street2', sa.String(length=100), nullable=True),
                    sa.Column('address_city', sa.String(length=60), nullable=True),
                    sa.Column('address_state', sa.String(length=2), nullable=True),
                    sa.Column('address_zipcode', sa.String(length=10), nullable=True),
                    sa.Column('address_type', sa.String(length=15), nullable=True),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['user_uuid'], [u'user.uuid'], name=u'pending_customer_fk_user'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # batch_custorder
    op.add_column(u'batch_custorder', sa.Column('pending_customer_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key(u'batch_custorder_fk_pending_customer', 'batch_custorder', 'pending_customer', ['pending_customer_uuid'], ['uuid'])

    # custorder
    op.add_column(u'custorder', sa.Column('pending_customer_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key(u'custorder_fk_pending_customer', 'custorder', 'pending_customer', ['pending_customer_uuid'], ['uuid'])


def downgrade():

    # custorder
    op.drop_constraint(u'custorder_fk_pending_customer', 'custorder', type_='foreignkey')
    op.drop_column(u'custorder', 'pending_customer_uuid')

    # batch_custorder
    op.drop_constraint(u'batch_custorder_fk_pending_customer', 'batch_custorder', type_='foreignkey')
    op.drop_column(u'batch_custorder', 'pending_customer_uuid')

    # pending_customer
    op.drop_table('pending_customer')
