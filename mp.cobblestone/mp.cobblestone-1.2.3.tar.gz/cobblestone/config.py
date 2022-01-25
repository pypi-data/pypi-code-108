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

PACKAGE_VERSION = '1.2.0'

# global config
# . auth
# (generated with: openssl rand -hex 32)
TOKEN_SECRET_KEY = os.getenv('TOKEN_SECRET_KEY')
TOKEN_ALGORITHM = 'HS256'
TOKEN_EXPIRE_MINUTES = 7 * 24 * 60  # one week token

# server config
ORIGINS_WHITELIST = []
