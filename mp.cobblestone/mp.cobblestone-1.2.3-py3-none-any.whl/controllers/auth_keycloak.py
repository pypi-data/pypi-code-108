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
import requests


KEYCLOAK_HOST = os.getenv('KEYCLOAK_HOST')
KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM')
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID')
KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET')

KEYCLOAK_BASE_URL = f'{KEYCLOAK_HOST}/auth/realms/{KEYCLOAK_REALM}/protocol/openid-connect'
TOKEN_ENDPOINT = f'{KEYCLOAK_BASE_URL}/token'
USER_INFO_ENDPOINT = f'{KEYCLOAK_BASE_URL}/userinfo'


def authenticate_user(username: str, password: str) -> dict:
    headers = {
        'Accept': 'application/json',
        'Accept-Charset': 'utf-8',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': KEYCLOAK_CLIENT_ID,
        'client_secret': KEYCLOAK_CLIENT_SECRET,
    }
    resp = requests.post(TOKEN_ENDPOINT, data=data, headers=headers)
    if resp.status_code != 200:
        print(resp.text)
        return None

    tok = resp.json()
    headers = {
        'Authorization': f'Bearer {tok["access_token"]}',
    }
    resp = requests.get(USER_INFO_ENDPOINT, headers=headers)
    if resp.status_code != 200:
        print(resp.text)
        return None

    user = resp.json()
    return {
        'uid': user['sub'],
        'username': user['preferred_username'],
        'firstname': user.get('given_name', ''),
        'lastname': user.get('family_name', ''),
        'email': user.get('email', ''),
        'roles': user.get('roles', []),
    }
