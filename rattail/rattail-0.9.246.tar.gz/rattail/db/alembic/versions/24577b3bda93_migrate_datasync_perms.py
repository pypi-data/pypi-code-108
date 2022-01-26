# -*- coding: utf-8; -*-
"""migrate datasync perms

Revision ID: 24577b3bda93
Revises: 678a32b6cb19
Create Date: 2021-12-06 10:17:33.048549

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '24577b3bda93'
down_revision = '678a32b6cb19'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types


permission = sa.sql.table('permission', sa.sql.column('permission'))


def rename_perm(oldname, newname):
    op.execute(permission.update()\
               .where(permission.c.permission == oldname)\
               .values({'permission': newname}))


def upgrade():
    rename_perm('datasync.bulk_delete', 'datasync_changes.bulk_delete')
    rename_perm('datasync.delete', 'datasync_changes.delete')
    rename_perm('datasync.list', 'datasync_changes.list')
    rename_perm('datasync.view', 'datasync_changes.view')


def downgrade():
    rename_perm('datasync_changes.bulk_delete', 'datasync.bulk_delete')
    rename_perm('datasync_changes.delete', 'datasync.delete')
    rename_perm('datasync_changes.list', 'datasync.list')
    rename_perm('datasync_changes.view', 'datasync.view')
