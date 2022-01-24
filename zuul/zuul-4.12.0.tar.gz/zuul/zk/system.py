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
import json
import logging
import uuid

from kazoo.exceptions import NoNodeError, NodeExistsError

from zuul.zk import ZooKeeperBase


# This is outside of the /zuul root, so this holds data we expect to
# be persistent (it will not be deleted by 'zuul delete-state').
SYSTEM_ROOT = "/zuul-system"


class ZuulSystem(ZooKeeperBase):
    """Information about the complete Zuul system

    Currently includes only a system UUID for use with Nodepool.
    """

    log = logging.getLogger("zuul.System")

    def __init__(self, client):
        super().__init__(client)
        try:
            data, stat = self.kazoo_client.get(SYSTEM_ROOT)
        except NoNodeError:
            system_id = uuid.uuid4().hex
            data = json.dumps({'system_id': system_id},
                              sort_keys=True).encode('utf8')
            try:
                self.kazoo_client.create(SYSTEM_ROOT, data)
            except NodeExistsError:
                data, stat = self.kazoo_client.get(SYSTEM_ROOT)

        self.system_id = json.loads(data.decode('utf8'))['system_id']
