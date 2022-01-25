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

from fastapi import FastAPI
import cobblestone.models as all_schemas
from cobblestone.helpers.autorouting import create_handlers, create_router

from .users import create_router as UsersRouter


def create_base_router(app: FastAPI):
    SCHEMAS_LIST = all_schemas.__all__
    for schema in SCHEMAS_LIST:
        raw_name = schema.lower()
        handlers = create_handlers(schema, raw_name)
        create_router(app, schema, raw_name, handlers)


def create_routers(app: FastAPI):
    UsersRouter(app)
