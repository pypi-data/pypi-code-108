# -*- coding: utf-8; -*-
"""rename batch_labels

Revision ID: 6a691bede834
Revises: 117236288811
Create Date: 2021-02-02 14:27:13.539293

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '6a691bede834'
down_revision = '117236288811'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # remove references to `label_batch`
    op.drop_constraint('label_batch_handheld_fk_batch', 'label_batch_handheld', type_='foreignkey')
    op.drop_constraint('label_batch_row_fk_batch', 'label_batch_row', type_='foreignkey')

    # batch_labels
    op.drop_constraint('label_batch_fk_created_by', 'label_batch', type_='foreignkey')
    op.drop_constraint('label_batch_fk_cognized_by', 'label_batch', type_='foreignkey')
    op.drop_constraint('label_batch_fk_executed_by', 'label_batch', type_='foreignkey')
    op.drop_constraint('label_batch_fk_handheld_batch', 'label_batch', type_='foreignkey')
    op.drop_constraint('label_batch_fk_label_profile', 'label_batch', type_='foreignkey')
    op.rename_table('label_batch', 'batch_labels')
    op.create_foreign_key('batch_labels_fk_created_by',
                          'batch_labels', 'user',
                          ['created_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_labels_fk_cognized_by',
                          'batch_labels', 'user',
                          ['cognized_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_labels_fk_executed_by',
                          'batch_labels', 'user',
                          ['executed_by_uuid'], ['uuid'])
    op.create_foreign_key('batch_labels_fk_handheld_batch',
                          'batch_labels', 'batch_handheld',
                          ['handheld_batch_uuid'], ['uuid'])
    op.create_foreign_key('batch_labels_fk_label_profile',
                          'batch_labels', 'label_profile',
                          ['label_profile_uuid'], ['uuid'])

    # batch_labels_handheld
    op.drop_constraint('label_batch_handheld_fk_handheld', 'label_batch_handheld', type_='foreignkey')
    op.rename_table('label_batch_handheld', 'batch_labels_handheld')
    op.create_foreign_key('batch_labels_handheld_fk_batch',
                          'batch_labels_handheld', 'batch_labels',
                          ['batch_uuid'], ['uuid'])
    op.create_foreign_key('batch_labels_handheld_fk_handheld',
                          'batch_labels_handheld', 'batch_handheld',
                          ['handheld_uuid'], ['uuid'])

    # batch_labels_row
    op.drop_constraint('label_batch_row_fk_product', 'label_batch_row', type_='foreignkey')
    op.drop_constraint('label_batch_row_fk_label_profile', 'label_batch_row', type_='foreignkey')
    op.rename_table('label_batch_row', 'batch_labels_row')
    op.create_foreign_key('batch_labels_row_fk_batch_uuid',
                          'batch_labels_row', 'batch_labels',
                          ['batch_uuid'], ['uuid'])
    op.create_foreign_key('batch_labels_row_fk_product',
                          'batch_labels_row', 'product',
                          ['product_uuid'], ['uuid'])
    op.create_foreign_key('batch_labels_row_fk_label_profile',
                          'batch_labels_row', 'label_profile',
                          ['label_profile_uuid'], ['uuid'])


def downgrade():

    # remove references to `batch_labels`
    op.drop_constraint('batch_labels_handheld_fk_batch', 'batch_labels_handheld', type_='foreignkey')
    op.drop_constraint('batch_labels_row_fk_batch_uuid', 'batch_labels_row', type_='foreignkey')

    # batch_labels
    op.drop_constraint('batch_labels_fk_created_by', 'batch_labels', type_='foreignkey')
    op.drop_constraint('batch_labels_fk_cognized_by', 'batch_labels', type_='foreignkey')
    op.drop_constraint('batch_labels_fk_executed_by', 'batch_labels', type_='foreignkey')
    op.drop_constraint('batch_labels_fk_handheld_batch', 'batch_labels', type_='foreignkey')
    op.drop_constraint('batch_labels_fk_label_profile', 'batch_labels', type_='foreignkey')
    op.rename_table('batch_labels', 'label_batch')
    op.create_foreign_key('label_batch_fk_created_by',
                          'label_batch', 'user',
                          ['created_by_uuid'], ['uuid'])
    op.create_foreign_key('label_batch_fk_cognized_by',
                          'label_batch', 'user',
                          ['cognized_by_uuid'], ['uuid'])
    op.create_foreign_key('label_batch_fk_executed_by',
                          'label_batch', 'user',
                          ['executed_by_uuid'], ['uuid'])
    op.create_foreign_key('label_batch_fk_handheld_batch',
                          'label_batch', 'batch_handheld',
                          ['handheld_batch_uuid'], ['uuid'])
    op.create_foreign_key('label_batch_fk_label_profile',
                          'label_batch', 'label_profile',
                          ['label_profile_uuid'], ['uuid'])

    # batch_labels_handheld
    op.drop_constraint('batch_labels_handheld_fk_handheld', 'batch_labels_handheld', type_='foreignkey')
    op.rename_table('batch_labels_handheld', 'label_batch_handheld')
    op.create_foreign_key('label_batch_handheld_fk_batch',
                          'label_batch_handheld', 'label_batch',
                          ['batch_uuid'], ['uuid'])
    op.create_foreign_key('label_batch_handheld_fk_handheld',
                          'label_batch_handheld', 'batch_handheld',
                          ['handheld_uuid'], ['uuid'])

    # batch_labels_row
    op.drop_constraint('batch_labels_row_fk_product', 'batch_labels_row', type_='foreignkey')
    op.drop_constraint('batch_labels_row_fk_label_profile', 'batch_labels_row', type_='foreignkey')
    op.rename_table('batch_labels_row', 'label_batch_row')
    op.create_foreign_key('label_batch_row_fk_batch',
                          'label_batch_row', 'label_batch',
                          ['batch_uuid'], ['uuid'])
    op.create_foreign_key('label_batch_row_fk_product',
                          'label_batch_row', 'product',
                          ['product_uuid'], ['uuid'])
    op.create_foreign_key('label_batch_row_fk_label_profile',
                          'label_batch_row', 'label_profile',
                          ['label_profile_uuid'], ['uuid'])
