# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""add build final column

Revision ID: 269691d2220e
Revises: e0eda5d09eae
Create Date: 2020-01-03 07:53:15.962739

"""

# revision identifiers, used by Alembic.
revision = '269691d2220e'
down_revision = '16c1dc9054d0'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

BUILD_TABLE = 'zuul_build'


def upgrade(table_prefix=''):
    op.add_column(table_prefix + BUILD_TABLE, sa.Column('final', sa.Boolean))

    # Set all existing build entries to final (otherwise they will vanish from
    # the UI)
    new_column = sa.table(table_prefix + BUILD_TABLE, sa.column('final'))
    op.execute(new_column.update().values(**{'final': True}))


def downgrade():
    raise Exception("Downgrades not supported")
