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

"""add held attribute to builds

Revision ID: 32e28a297c3e
Revises: 16c1dc9054d0
Create Date: 2020-05-19 11:19:19.263236

"""

# revision identifiers, used by Alembic.
revision = '32e28a297c3e'
down_revision = '269691d2220e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade(table_prefix=''):
    op.add_column(
        table_prefix + 'zuul_build',
        sa.Column('held', sa.Boolean)
    )


def downgrade():
    raise Exception("Downgrades not supported")
