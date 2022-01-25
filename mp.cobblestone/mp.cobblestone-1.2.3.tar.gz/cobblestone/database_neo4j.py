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
from neomodel import config

import cobblestone.models as all_schemas
from cobblestone.helpers.converters import wrap_additional_fields

NEO4J_USER = os.getenv('DB_USER')
NEO4J_PASSWORD = os.getenv('DB_PASSWORD')
NEO4J_HOST = os.getenv('DB_HOST', '0.0.0.0')
NEO4J_BOLT_PORT = os.getenv('DB_PORT', '7687')
if NEO4J_USER and NEO4J_PASSWORD:
    NEO4J_DB_URL = f'bolt://{NEO4J_USER}:{NEO4J_PASSWORD}@{NEO4J_HOST}:{NEO4J_BOLT_PORT}'
else:
    NEO4J_DB_URL = f'bolt://{NEO4J_HOST}:{NEO4J_BOLT_PORT}'

print(f'Connecting to Neo4j DB (@{NEO4J_HOST}:{NEO4J_BOLT_PORT})')
config.DATABASE_URL = NEO4J_DB_URL


def initialize_database_metadata():
    wrap_additional_fields(all_schemas.__all__)
