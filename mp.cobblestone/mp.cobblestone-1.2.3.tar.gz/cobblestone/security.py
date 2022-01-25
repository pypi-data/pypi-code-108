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

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

invalid_auth_exception = HTTPException(
    status_code=401,
    detail='invalid-auth',
    headers={'WWW-Authenticate': 'Bearer'},
)
invalid_token_exception = HTTPException(
    status_code=403,
    detail='invalid-token',
    headers={'WWW-Authenticate': 'Bearer'},
)
credentials_exception = HTTPException(
    status_code=401,
    detail='expired-token',
    headers={'WWW-Authenticate': 'Bearer'},
)
roles_exception = HTTPException(
    status_code=401,
    detail='invalid-roles',
    headers={'WWW-Authenticate': 'Bearer'},
)


def check_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return password_context.hash(password)
