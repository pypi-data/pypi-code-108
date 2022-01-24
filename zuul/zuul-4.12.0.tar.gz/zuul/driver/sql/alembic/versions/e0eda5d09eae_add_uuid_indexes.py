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

"""add_uuid_indexes

Revision ID: e0eda5d09eae
Revises: c18b1277dfb5
Create Date: 2019-07-24 16:04:18.042209

"""

# revision identifiers, used by Alembic.
revision = 'e0eda5d09eae'
down_revision = 'c18b1277dfb5'
branch_labels = None
depends_on = None

from alembic import op

BUILDSET_TABLE = 'zuul_buildset'
BUILD_TABLE = 'zuul_build'


def upgrade(table_prefix=''):
    prefixed_buildset = table_prefix + BUILDSET_TABLE
    prefixed_build = table_prefix + BUILD_TABLE

    # To look up a build by uuid. buildset_id is included
    # so that it's a covering index and can satisfy the join back to buildset
    # without an additional lookup.
    op.create_index(
        table_prefix + 'uuid_buildset_id_idx', prefixed_build,
        ['uuid', 'buildset_id'])

    # To look up a buildset by uuid.
    op.create_index(table_prefix + 'uuid_idx', prefixed_buildset, ['uuid'])


def downgrade():
    raise Exception("Downgrades not supported")
