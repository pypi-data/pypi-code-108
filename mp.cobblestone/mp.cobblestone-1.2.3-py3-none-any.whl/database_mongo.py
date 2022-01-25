# -----------------------------------------------------------------------
# Copyright 2020 Mina Pêcheux

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at the root of the repo.

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------

import os
from mongoengine import connect

import cobblestone.models as all_schemas
from cobblestone.helpers.converters import wrap_additional_fields

MONGO_USER = os.getenv('DB_USER')
MONGO_PASSWORD = os.getenv('DB_PASSWORD')
MONGO_NAME = os.getenv('DB_NAME')
MONGO_HOST = os.getenv('DB_HOST', '0.0.0.0')
MONGO_PORT = int(os.getenv('DB_PORT', '27017'))
print(f'Connecting to Mongo DB ({MONGO_NAME} - @{MONGO_HOST}:{MONGO_PORT})')

url_options = f'{MONGO_HOST}:{MONGO_PORT}'
if MONGO_USER and MONGO_PASSWORD:
    url_options = f'{MONGO_USER}:{MONGO_PASSWORD}@{url_options}'

db = connect(
    MONGO_NAME,
    host=f'mongodb://{url_options}',
    authentication_source='admin'
)


def initialize_database_metadata():
    wrap_additional_fields(all_schemas.__all__)
