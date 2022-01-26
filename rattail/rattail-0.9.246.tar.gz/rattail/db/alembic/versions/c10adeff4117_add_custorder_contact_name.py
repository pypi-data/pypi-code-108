# -*- coding: utf-8; -*-
"""add custorder.contact_name

Revision ID: c10adeff4117
Revises: 5a256a77e6d0
Create Date: 2021-10-07 11:05:10.561894

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'c10adeff4117'
down_revision = u'5a256a77e6d0'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_custorder
    op.add_column('batch_custorder', sa.Column('contact_name', sa.String(length=100), nullable=True))

    # custorder
    op.add_column('custorder', sa.Column('contact_name', sa.String(length=100), nullable=True))


def downgrade():
    
    # custorder
    op.drop_column('custorder', 'contact_name')
    
    # batch_custorder
    op.drop_column('batch_custorder', 'contact_name')
