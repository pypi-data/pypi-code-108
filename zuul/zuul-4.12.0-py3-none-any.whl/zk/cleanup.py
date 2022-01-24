# Copyright 2021 Acme Gating, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import kazoo.recipe.lock


class SemaphoreCleanupLock(kazoo.recipe.lock.Lock):
    _path = '/zuul/cleanup/sempahores'

    def __init__(self, client):
        super().__init__(client.client, self._path)


class BuildRequestCleanupLock(kazoo.recipe.lock.Lock):
    _path = '/zuul/cleanup/build_requests'

    def __init__(self, client):
        super().__init__(client.client, self._path)


class MergeRequestCleanupLock(kazoo.recipe.lock.Lock):
    _path = '/zuul/cleanup/merge_requests'

    def __init__(self, client):
        super().__init__(client.client, self._path)


class ConnectionCleanupLock(kazoo.recipe.lock.Lock):
    _path = '/zuul/cleanup/connection'

    def __init__(self, client):
        super().__init__(client.client, self._path)


class GeneralCleanupLock(kazoo.recipe.lock.Lock):
    _path = '/zuul/cleanup/general'

    def __init__(self, client):
        super().__init__(client.client, self._path)


class NodeRequestCleanupLock(kazoo.recipe.lock.Lock):
    _path = '/zuul/cleanup/node_request'

    def __init__(self, client):
        super().__init__(client.client, self._path)
