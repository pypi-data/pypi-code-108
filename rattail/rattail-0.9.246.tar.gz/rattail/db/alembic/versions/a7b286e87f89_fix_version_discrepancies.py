# -*- coding: utf-8; -*-
"""fix version discrepancies

Revision ID: a7b286e87f89
Revises: 8f9a960b0c5e
Create Date: 2021-01-23 19:24:03.780728

"""

# revision identifiers, used by Alembic.
revision = 'a7b286e87f89'
down_revision = '8f9a960b0c5e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types


# NOTE: i apparently just missed these somewhere along the way.  hopefully they
# were the only "gaps" but i don't really know that for sure...  this should
# cover all "grow field X" type migrations though, i believe.

def upgrade():

    # role
    op.alter_column('role_version', 'name', type_=sa.String(length=100))

    # category
    op.alter_column('category_version', 'code', type_=sa.String(length=20))

    # label_profile
    op.alter_column('label_profile_version', 'code', type_=sa.String(length=30))


def downgrade():

    # label_profile
    op.alter_column('label_profile_version', 'code', type_=sa.String(length=3))

    # category
    op.alter_column('category_version', 'code', type_=sa.String(length=8))

    # role
    op.alter_column('role_version', 'name', type_=sa.String(length=25))
