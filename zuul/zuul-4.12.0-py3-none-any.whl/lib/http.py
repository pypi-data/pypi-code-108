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

import socket

from requests.adapters import HTTPAdapter
from urllib3.connection import HTTPConnection


class ZuulHTTPAdapter(HTTPAdapter):
    "A requests HTTPAdapter class which supports TCP keepalives"
    def __init__(self, *args, **kw):
        self.keepalive = int(kw.pop('keepalive', 0))
        super().__init__(*args, **kw)

    def init_poolmanager(self, *args, **kw):
        if self.keepalive:
            ka = self.keepalive
            kw['socket_options'] = HTTPConnection.default_socket_options + [
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, ka),
                (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, ka),
                (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 2),
            ]
        return super().init_poolmanager(*args, **kw)
