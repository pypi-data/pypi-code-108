# Copyright 2018 Red Hat, Inc.
#
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

"""Change missing build url to null

Revision ID: 52d49e1bfe22
Revises: e0eda5d09eae
Create Date: 2018-03-18 09:30:23.343650

"""

# revision identifiers, used by Alembic.
revision = '52d49e1bfe22'
down_revision = '32e28a297c3e'
branch_labels = None
depends_on = None

BUILD_TABLE = 'zuul_build'

from alembic import op


def upgrade(table_prefix=''):
    op.execute(
        'UPDATE {table_name} SET log_url=NULL WHERE log_url=job_name'.format(
            table_name=table_prefix + BUILD_TABLE))


def downgrade(table_prefix=''):
    raise Exception("Downgrades not supported")
