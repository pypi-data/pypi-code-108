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

import cobblestone.models as all_schemas
from cobblestone.database import session_scope
import argparse
import importlib
import os
import requests


from dotenv import load_dotenv
load_dotenv()


api_host = os.environ.get('API_HOST', '127.0.0.1')
api_port = os.environ.get('API_PORT', 8000)
BASE_URL = f'http://{api_host}:{api_port}'
CONFIG = {
    'headers': None,
}


def get_token(data: dict) -> str:
    resp = requests.post(BASE_URL + '/token', data=data)
    return resp.json()['access_token']


def drop_db():
    print('Dropping database')
    with session_scope() as session:
        SCHEMAS_LIST = all_schemas.__all__
        for schema in SCHEMAS_LIST:
            raw_name = schema.lower()
            schemas_module = importlib.import_module(
                '.' + raw_name, 'cobblestone.models')
            db_schema = getattr(schemas_module, schema + 'InDB')
            session.query(db_schema).delete()


# USERS
def create_unprotected_user(data: dict) -> dict:
    resp = requests.post(BASE_URL + '/users-unprotected', json=data)
    return resp.json()


def create_user(data: dict) -> dict:
    resp = requests.post(BASE_URL + '/users', json=data,
                         headers=CONFIG['headers'])
    return resp.json()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--users', type=str, nargs='+')
    args = parser.parse_args()

    drop_db()

    admin_user = create_unprotected_user(
        {'username': 'admin', 'firstname': 'Admin', 'lastname': 'Admin'})
    token = get_token(
        {'username': admin_user['username'], 'password': admin_user['username']})
    CONFIG['headers'] = {'Authorization': 'Bearer {}'.format(token)}

    if args.users:
        for user in args.users:
            username, pwd = user.split(':')
            name = username.title()
            create_user({
                'username': username,
                'firstname': name,
                'lastname': name,
                'password': pwd,
            })
