# Copyright 2012 Google Inc.
# Copyright 2019 Red Hat, Inc.
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

import logging
import requests
import threading
import time

TOKEN_URL = ('http://metadata.google.internal/computeMetadata/'
             'v1/instance/service-accounts/default/token')
REFRESH = 25
RETRY_INTERVAL = 5


class GCloudAuth(requests.auth.AuthBase):
    log = logging.getLogger('zuul.GerritConnection')

    def __init__(self, user, password):
        self.token = None
        self.expires = 0
        try:
            self.getToken()
        except Exception:
            self.log.exception("Error updating token:")
        self.update_thread = threading.Thread(target=self.update)
        self.update_thread.daemon = True
        self.update_thread.start()

    def update(self):
        while True:
            try:
                self._update()
            except Exception:
                self.log.exception("Error updating token:")
                time.sleep(5)

    def _update(self):
        now = time.time()
        expires = self.expires - REFRESH
        expires = max(expires, now + RETRY_INTERVAL)
        while now < expires:
            time.sleep(expires - now)
            now = time.time()
        self.getToken()

    def getToken(self):
        r = requests.get(TOKEN_URL, headers={'Metadata-Flavor': 'Google'})
        data = r.json()
        self.token = data['access_token']
        self.expires = time.time() + data['expires_in']

    def __call__(self, request):
        request.prepare_cookies({'o': self.token})
        return request
