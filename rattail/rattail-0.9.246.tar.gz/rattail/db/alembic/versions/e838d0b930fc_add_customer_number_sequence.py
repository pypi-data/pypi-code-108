# -*- coding: utf-8; -*-
"""add customer number sequence

Revision ID: e838d0b930fc
Revises: 3ed719791439
Create Date: 2019-10-22 16:10:32.699424

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'e838d0b930fc'
down_revision = u'3ed719791439'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types


# we are creating this in the hopes that it may be useful, but we are *not*
# wiring it up, e.g. to provide default values for the Customer.number field -
# you must do that within your own app logic if you want that behavior
customer_number_seq = sa.Sequence('customer_number_seq')


def upgrade():
    from sqlalchemy.schema import CreateSequence

    # customer_number_seq
    op.execute(CreateSequence(customer_number_seq))


def downgrade():
    from sqlalchemy.schema import DropSequence

    # customer_number_seq
    op.execute(DropSequence(customer_number_seq))
