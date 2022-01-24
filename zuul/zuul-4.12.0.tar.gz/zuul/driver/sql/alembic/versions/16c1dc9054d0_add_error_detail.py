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

"""add error_detail

Revision ID: 16c1dc9054d0
Revises: 5f183546b39c
Create Date: 2020-02-25 14:04:56.947095

"""

# revision identifiers, used by Alembic.
revision = '16c1dc9054d0'
down_revision = '5f183546b39c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade(table_prefix=''):
    op.add_column(
        table_prefix + 'zuul_build', sa.Column('error_detail', sa.TEXT()))


def downgrade():
    raise Exception("Downgrades not supported")
