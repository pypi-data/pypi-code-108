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

from pydantic import BaseModel
from typing import List, Optional

from cobblestone.helpers.converters import PydanticToORM
from cobblestone.security import hash_password


class User(BaseModel):
    username: str
    firstname: str = ''
    lastname: str = ''
    email: str = ''


class UserPayload(User):
    password: Optional[str] = None


class UserFull(User):
    uid: str


class UserProtected(UserFull):
    password: str


def make_password(u: dict) -> str:
    p = u.get('password')
    if not p:
        p = u['username']
    return hash_password(p.encode())


UserInDB = PydanticToORM(UserProtected, 'User',
                         constructors={
                             'password': make_password,
                         })


class UserToken(BaseModel):
    access_token: str
    token_type: str


class UserTokenData(UserFull):
    roles: List[str] = []
