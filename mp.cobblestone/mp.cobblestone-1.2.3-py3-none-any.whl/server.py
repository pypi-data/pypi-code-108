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

from cobblestone.routes import create_base_router, create_routers
from cobblestone.config import ORIGINS_WHITELIST, PACKAGE_VERSION
from cobblestone.database import initialize_database_metadata

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS_WHITELIST,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class ApiVersion(BaseModel):
    version: str


@app.get('/version', response_model=ApiVersion)
async def get_version() -> dict:
    return {'version': PACKAGE_VERSION}

create_base_router(app)
create_routers(app)
initialize_database_metadata()
