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

"""add event id column

Revision ID: 5f183546b39c
Revises: e0eda5d09eae
Create Date: 2019-12-05 13:33:30.155447

"""

# revision identifiers, used by Alembic.
revision = '5f183546b39c'
down_revision = 'e0eda5d09eae'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade(table_prefix=''):
    op.add_column(
        table_prefix + "zuul_buildset",
        sa.Column("event_id", sa.String(255), nullable=True)
    )


def downgrade():
    raise Exception("Downgrades not supported")
