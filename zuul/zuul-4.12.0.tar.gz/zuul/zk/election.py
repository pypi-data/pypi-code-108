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

from kazoo.protocol.states import KazooState
from kazoo.recipe.election import Election


class SessionAwareElection(Election):
    def __init__(self, client, path, identifier=None):
        self._zuul_session_expired = False
        super().__init__(client, path, identifier)

    def run(self, func, *args, **kwargs):
        self._zuul_session_expired = False
        self.lock.client.add_listener(self._zuul_session_watcher)
        try:
            return super().run(func, *args, **kwargs)
        finally:
            self.lock.client.remove_listener(self._zuul_session_watcher)

    def _zuul_session_watcher(self, state):
        if state == KazooState.LOST:
            self._zuul_session_expired = True

    def is_still_valid(self):
        return not self._zuul_session_expired
