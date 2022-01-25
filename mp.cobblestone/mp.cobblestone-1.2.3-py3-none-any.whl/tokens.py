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

from typing import List, Optional
from datetime import datetime, timedelta

from jose import jwt

from cobblestone.config import TOKEN_SECRET_KEY, TOKEN_ALGORITHM, TOKEN_EXPIRE_MINUTES
from cobblestone.security import credentials_exception, roles_exception, invalid_token_exception


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, TOKEN_SECRET_KEY, algorithm=TOKEN_ALGORITHM)
    return encoded_jwt


def get_access_token(user_data: dict):
    t = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return create_access_token(data=user_data, expires_delta=t)


def decode_token(token: str):
    try:
        return jwt.decode(token, TOKEN_SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
    except:
        raise invalid_token_exception


def check_token(token: str, roles: List[str] = []) -> str:
    if token is None:
        raise credentials_exception
    payload = decode_token(token)
    if payload.get('username') is None or payload.get('uid') is None:
        raise credentials_exception
    if len(roles) > 0:
        common_roles = set(roles).intersection(set(payload.get('roles', [])))
        if len(common_roles) == 0:
            raise roles_exception
    return payload.get('uid')
