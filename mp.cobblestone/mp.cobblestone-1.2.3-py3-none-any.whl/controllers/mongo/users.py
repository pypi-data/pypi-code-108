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

from mongoengine import DoesNotExist, MultipleObjectsReturned
from cobblestone.models.user import UserInDB
from cobblestone.helpers.utils import PRIMARY_KEY, create_uid


def get_user_by_uid(user_uid: str) -> dict:
    user = UserInDB.objects(uid=user_uid).get()
    if user:
        return user.to_json()


def get_user(username: str) -> dict:
    try:
        user = UserInDB.objects(username=username).get()
        return user.to_json()
    except (DoesNotExist, MultipleObjectsReturned):
        return None


def create_user(data: dict) -> dict:
    data[PRIMARY_KEY] = create_uid()
    for k, v in getattr(UserInDB, '_constructors').items():
        data[k] = v(data)
    instance = UserInDB(**data).save()
    return instance.to_json()
