# -*- coding: utf-8; -*-
"""add merge_request_people

Revision ID: 51f7773bb07a
Revises: 9072c76a3afc
Create Date: 2021-08-19 10:24:09.801411

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '51f7773bb07a'
down_revision = u'9072c76a3afc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # merge_request_people
    op.create_table('merge_request_people',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('removing_uuid', sa.String(length=32), nullable=False),
                    sa.Column('keeping_uuid', sa.String(length=32), nullable=False),
                    sa.Column('requested', sa.DateTime(), nullable=False),
                    sa.Column('requested_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('merged', sa.DateTime(), nullable=True),
                    sa.Column('merged_by_uuid', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['merged_by_uuid'], [u'user.uuid'], name=u'merge_request_people_fk_merged_by'),
                    sa.ForeignKeyConstraint(['requested_by_uuid'], [u'user.uuid'], name=u'merge_request_people_fk_requested_by'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # merge_request_people
    op.drop_table('merge_request_people')
