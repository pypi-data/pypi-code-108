# Copyright 2020 BMW Group
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
from collections.abc import MutableMapping
from functools import total_ordering

from kazoo.exceptions import NoNodeError

from zuul.zk import ZooKeeperBase


@total_ordering
class LayoutState:
    """Representation of a tenant's layout state.

    The layout state holds information about a certain version of a
    tenant's layout. It is used to coordinate reconfigurations across
    multiple schedulers by comparing a local tenant layout state
    against the current version in Zookeeper. In case it detects that
    a local layout state is outdated, this scheduler is not allowed to
    process this tenant (events, pipelines, ...) until the layout is
    updated.

    The important information of the layout state is the logical
    timestamp (ltime) that is used to detect if the layout on a
    scheduler needs to be updated. The ltime is the last modified
    transaction ID (mzxid) of the corresponding Znode in Zookeeper.

    The hostname of the scheduler creating the new layout state and the
    timestamp of the last reconfiguration are only informational and
    may aid in debugging.
    """

    def __init__(self, tenant_name, hostname, last_reconfigured, uuid,
                 branch_cache_min_ltimes, ltime=-1):
        self.uuid = uuid
        self.ltime = ltime
        self.tenant_name = tenant_name
        self.hostname = hostname
        self.last_reconfigured = last_reconfigured
        self.branch_cache_min_ltimes = branch_cache_min_ltimes

    def toDict(self):
        return {
            "tenant_name": self.tenant_name,
            "hostname": self.hostname,
            "last_reconfigured": self.last_reconfigured,
            "uuid": self.uuid,
            "branch_cache_min_ltimes": self.branch_cache_min_ltimes,
        }

    @classmethod
    def fromDict(cls, data):
        return cls(
            data["tenant_name"],
            data["hostname"],
            data["last_reconfigured"],
            data.get("uuid"),
            data.get("branch_cache_min_ltimes"),
            data.get("ltime", -1),
        )

    def __eq__(self, other):
        if not isinstance(other, LayoutState):
            return False
        return self.uuid == other.uuid

    def __gt__(self, other):
        if not isinstance(other, LayoutState):
            return False
        return self.ltime > other.ltime

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} {self.tenant_name}: "
            f"ltime={self.ltime}, "
            f"hostname={self.hostname}, "
            f"last_reconfigured={self.last_reconfigured}>"
        )


class LayoutStateStore(ZooKeeperBase, MutableMapping):

    layout_root = "/zuul/layout"

    def __init__(self, client, callback):
        super().__init__(client)
        self._watched_tenants = set()
        self._callback = callback
        self.kazoo_client.ensure_path(self.layout_root)
        self.kazoo_client.ChildrenWatch(self.layout_root, self._layoutCallback)

    def _layoutCallback(self, tenant_list, event=None):
        new_tenants = set(tenant_list) - self._watched_tenants
        for tenant_name in new_tenants:
            self.kazoo_client.DataWatch(f"{self.layout_root}/{tenant_name}",
                                        self._callbackWrapper)

    def _callbackWrapper(self, data, stat, event):
        self._callback()

    def __getitem__(self, tenant_name):
        try:
            data, zstat = self.kazoo_client.get(
                f"{self.layout_root}/{tenant_name}")
        except NoNodeError:
            raise KeyError(tenant_name)

        if not data:
            raise KeyError(tenant_name)

        return LayoutState.fromDict({
            "ltime": zstat.last_modified_transaction_id,
            **json.loads(data)
        })

    def __setitem__(self, tenant_name, state):
        path = f"{self.layout_root}/{tenant_name}"
        data = json.dumps(state.toDict(), sort_keys=True).encode("utf-8")
        if self.kazoo_client.exists(path):
            zstat = self.kazoo_client.set(path, data)
        else:
            _, zstat = self.kazoo_client.create(path, data, include_data=True)
        # Set correct ltime of the layout in Zookeeper
        state.ltime = zstat.last_modified_transaction_id

    def __delitem__(self, tenant_name):
        try:
            self.kazoo_client.delete(f"{self.layout_root}/{tenant_name}")
        except NoNodeError:
            raise KeyError(tenant_name)

    def __iter__(self):
        try:
            tenant_names = self.kazoo_client.get_children(self.layout_root)
        except NoNodeError:
            return
        yield from tenant_names

    def __len__(self):
        zstat = self.kazoo_client.exists(self.layout_root)
        if zstat is None:
            return 0
        return zstat.children_count
