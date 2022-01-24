# Copyright 2021 BMW Group
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

import contextlib
import json
import logging

from collections.abc import MutableMapping
from urllib.parse import quote_plus, unquote_plus

from kazoo.exceptions import NoNodeError

from zuul import model
from zuul.zk import sharding, ZooKeeperSimpleBase
from zuul.zk.vendor import lock

CONFIG_ROOT = "/zuul/config"


def _safe_path(root_path, *keys):
    return "/".join((root_path, *(quote_plus(k) for k in keys)))


class FilesCache(ZooKeeperSimpleBase, MutableMapping):
    """Cache of raw config files in Zookeeper for a project-branch.

    Data will be stored in Zookeeper using the following path:
        /zuul/config/<project>/<branch>/<filename>

    """
    log = logging.getLogger("zuul.zk.config_cache.FilesCache")

    def __init__(self, client, root_path):
        super().__init__(client)
        self.root_path = root_path
        self.files_path = f"{root_path}/files"

    def setValidFor(self, extra_config_files, extra_config_dirs, ltime):
        """Set the cache valid for the given extra config files/dirs."""
        data = {
            "extra_files_searched": list(extra_config_files),
            "extra_dirs_searched": list(extra_config_dirs),
            "ltime": ltime,
        }
        payload = json.dumps(data, sort_keys=True).encode("utf8")
        try:
            self.kazoo_client.set(self.root_path, payload)
        except NoNodeError:
            self.kazoo_client.create(self.root_path, payload, makepath=True)

    def isValidFor(self, tpc, min_ltime):
        """Check if the cache is valid.

        Check if the cache is valid for the given tenant project config
        (tpc) and that it is up-to-date, relative to the give logical
        timestamp.

        """
        try:
            data, _ = self.kazoo_client.get(self.root_path)
        except NoNodeError:
            return False

        try:
            content = json.loads(data)
            extra_files_searched = set(content["extra_files_searched"])
            extra_dirs_searched = set(content["extra_dirs_searched"])
            ltime = content["ltime"]
        except Exception:
            return False

        if ltime < min_ltime:
            # Cache is outdated
            return False

        return (set(tpc.extra_config_files) <= extra_files_searched
                and set(tpc.extra_config_dirs) <= extra_dirs_searched)

    @property
    def ltime(self):
        try:
            data, _ = self.kazoo_client.get(self.root_path)
            content = json.loads(data)
            return content["ltime"]
        except Exception:
            return -1

    def _key_path(self, key):
        return _safe_path(self.files_path, key)

    def __getitem__(self, key):
        try:
            with sharding.BufferedShardReader(
                self.kazoo_client, self._key_path(key)
            ) as stream:
                return stream.read().decode("utf8")
        except NoNodeError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        path = self._key_path(key)
        with sharding.BufferedShardWriter(self.kazoo_client, path) as stream:
            stream.truncate(0)
            stream.write(value.encode("utf8"))

    def __delitem__(self, key):
        try:
            self.kazoo_client.delete(self._key_path(key), recursive=True)
        except NoNodeError:
            raise KeyError(key)

    def __iter__(self):
        try:
            children = self.kazoo_client.get_children(self.files_path)
        except NoNodeError:
            children = []
        yield from sorted(unquote_plus(c) for c in children)

    def __len__(self):
        try:
            children = self.kazoo_client.get_children(self.files_path)
        except NoNodeError:
            children = []
        return len(children)

    def clear(self):
        with contextlib.suppress(NoNodeError):
            self.kazoo_client.delete(self.root_path, recursive=True)


class UnparsedConfigCache(ZooKeeperSimpleBase):
    """Zookeeper cache for unparsed config files."""

    log = logging.getLogger("zuul.zk.config_cache.UnparsedConfigCache")

    def __init__(self, client, config_root=CONFIG_ROOT):
        super().__init__(client)
        self.cache_path = f"{config_root}/cache"
        self.lock_path = f"{config_root}/lock"

    def readLock(self, project_cname):
        return lock.ReadLock(
            self.kazoo_client, _safe_path(self.lock_path, project_cname))

    def writeLock(self, project_cname):
        return lock.WriteLock(
            self.kazoo_client, _safe_path(self.lock_path, project_cname))

    def getFilesCache(self, project_cname, branch_name):
        path = _safe_path(self.cache_path, project_cname, branch_name)
        return FilesCache(self.client, path)

    def listCachedProjects(self):
        try:
            children = self.kazoo_client.get_children(self.cache_path)
        except NoNodeError:
            children = []
        yield from sorted(unquote_plus(c) for c in children)

    def clearCache(self, project_cname, branch_name=None):
        if branch_name is None:
            path = _safe_path(self.cache_path, project_cname)
        else:
            path = _safe_path(self.cache_path, project_cname, branch_name)
        with contextlib.suppress(NoNodeError):
            self.kazoo_client.delete(path, recursive=True)


class SystemConfigCache(ZooKeeperSimpleBase):
    """Zookeeper cache for Zuul system configuration.

    The system configuration consists of the unparsed abide config and
    the runtime related settings from the Zuul config file.
    """

    SYSTEM_ROOT = "/zuul/system"
    log = logging.getLogger("zuul.zk.SystemConfigCache")

    def __init__(self, client, callback):
        super().__init__(client)
        self.conf_path = f"{self.SYSTEM_ROOT}/conf"
        self.lock_path = f"{self.SYSTEM_ROOT}/conf-lock"
        self._callback = callback
        self.kazoo_client.DataWatch(self.conf_path, self._configChanged)

    def _configChanged(self, data, stat, event):
        self._callback()

    @property
    def ltime(self):
        with lock.ReadLock(self.kazoo_client, self.lock_path):
            zstat = self.kazoo_client.exists(self.conf_path)
        return -1 if zstat is None else zstat.last_modified_transaction_id

    @property
    def is_valid(self):
        return self.ltime > -1

    def get(self):
        """Get the system configuration from Zookeeper.

        :returns: A tuple (unparsed abide config, system attributes)
        """
        with lock.ReadLock(self.kazoo_client, self.lock_path):
            try:
                with sharding.BufferedShardReader(
                    self.kazoo_client, self.conf_path
                ) as stream:
                    data = json.loads(stream.read())
            except Exception:
                raise RuntimeError("No valid system config")
            zstat = self.kazoo_client.exists(self.conf_path)
            return (model.UnparsedAbideConfig.fromDict(
                    data["unparsed_abide"],
                    ltime=zstat.last_modified_transaction_id
                ), model.SystemAttributes.fromDict(data["system_attributes"]))

    def set(self, unparsed_abide, system_attributes):
        with lock.WriteLock(self.kazoo_client, self.lock_path):
            data = {
                "unparsed_abide": unparsed_abide.toDict(),
                "system_attributes": system_attributes.toDict(),
            }
            with sharding.BufferedShardWriter(
                self.kazoo_client, self.conf_path
            ) as stream:
                stream.truncate(0)
                stream.write(json.dumps(data, sort_keys=True).encode("utf8"))
            zstat = self.kazoo_client.exists(self.conf_path)
            unparsed_abide.ltime = zstat.last_modified_transaction_id
