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

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

from cobblestone.models.user import UserPayload, UserProtected, UserFull, UserToken, UserTokenData
from cobblestone.controllers.auth import authenticate_user
from cobblestone.controllers.users import create_user, get_user_by_uid
from cobblestone.tokens import check_token, decode_token, get_access_token
from cobblestone.security import (credentials_exception,
                                  invalid_auth_exception,
                                  oauth2_scheme)

AUTH_METHOD = os.getenv('AUTH_METHOD')


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserProtected:
    try:
        payload = decode_token(token)
        if payload.get('username') is None or payload.get('uid') is None:
            raise credentials_exception
        token_data = UserTokenData(**payload)
    except JWTError:
        raise credentials_exception
    return token_data


def create_router(app):

    @app.get('/users-me', tags=['users'], response_model=UserTokenData)
    async def read_users_me(current_user: UserProtected = Depends(get_current_user)) -> UserTokenData:
        return current_user

    @app.post('/token', response_model=UserToken)
    async def token(form_data: OAuth2PasswordRequestForm = Depends()) -> UserToken:
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise invalid_auth_exception
        access_token = get_access_token(user)
        return {'access_token': access_token, 'token_type': 'bearer'}

    @app.patch('/token', response_model=UserToken)
    async def update_token(token: str = Depends(oauth2_scheme)) -> UserToken:
        user = check_token(token)
        updated_user = get_user_by_uid(user)
        access_token = get_access_token(updated_user)
        return {'access_token': access_token, 'token_type': 'bearer'}

    if AUTH_METHOD == 'db':

        @app.post(
            '/users-unprotected',
            response_model=UserFull,
            include_in_schema=False,
            status_code=201,
        )
        async def create_user_unprotected(data: UserPayload) -> UserFull:
            return create_user(data.dict())
