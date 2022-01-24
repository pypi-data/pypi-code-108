# Copyright 2014 Rackspace Australia
# Copyright 2021 BMW Group
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
import logging
import json

from zuul.zk.zkobject import ZKContext, ShardedZKObject
from zuul.zk.locks import SessionAwareReadLock, SessionAwareWriteLock, locked

from kazoo.exceptions import NoNodeError


class BranchCacheZKObject(ShardedZKObject):
    """Store the branch cache in ZK

    There are two projects dictionaries, protected and remainder.

    Each is project_name:str -> branches:list.

    The protected dictionary contains only the protected branches.

    The remainder dictionary contains any other branches.

    If there has never been a query that included unprotected
    branches, the projects key will not be present in the remaider
    dictionary.  If there has never been a query that excluded
    unprotected branches, then the protected dictionary will not have
    the project's key.

    If a project is absent from the dict, it needs to be queried from
    the source.

    When performing an exclude_unprotected query, remove any duplicate
    branches from remaider to save space.  When determining the full
    list of branches, combine both lists.
    """

    # We can always recreate data if necessary, so go ahead and
    # truncate when we update so we avoid corrupted data.
    truncate_on_create = True

    def getPath(self):
        return self._path

    def __init__(self):
        super().__init__()
        self._set(protected={},
                  remainder={})

    def serialize(self):
        data = {
            "protected": self.protected,
            "remainder": self.remainder,
        }
        return json.dumps(data, sort_keys=True).encode("utf8")

    def _save(self, context, data, create=False):
        super()._save(context, data, create)
        zstat = context.client.exists(self.getPath())
        self._set(_zstat=zstat)

    def _load(self, context, path=None):
        super()._load(context, path)
        zstat = context.client.exists(self.getPath())
        self._set(_zstat=zstat)


class BranchCache:
    def __init__(self, zk_client, connection):
        self.log = logging.getLogger(
            f"zuul.BranchCache.{connection.connection_name}")

        self.connection = connection

        cname = self.connection.connection_name
        base_path = f'/zuul/cache/connection/{cname}/branches'
        lock_path = f'{base_path}/lock'
        data_path = f'{base_path}/data'

        self.rlock = SessionAwareReadLock(zk_client.client, lock_path)
        self.wlock = SessionAwareWriteLock(zk_client.client, lock_path)

        # TODO: standardize on a stop event for connections and add it
        # to the context.
        self.zk_context = ZKContext(zk_client, self.wlock, None, self.log)

        with locked(self.wlock):
            try:
                self.cache = BranchCacheZKObject.fromZK(
                    self.zk_context, data_path, _path=data_path)
            except NoNodeError:
                self.cache = BranchCacheZKObject.new(
                    self.zk_context, _path=data_path)

    def getProjectBranches(self, project_name, exclude_unprotected,
                           min_ltime=-1):
        """Get the branch names for the given project.

        :param str project_name:
            The project for which the branches are returned.
        :param bool exclude_unprotected:
            Whether to return all or only protected branches.
        :param int min_ltime:
            The minimum cache ltime to consider the cache valid.

        :returns: The list of branch names, or None if the cache
            cannot satisfy the request.
        """
        if self.ltime < min_ltime:
            with locked(self.rlock):
                self.cache.refresh(self.zk_context)

        protected_branches = self.cache.protected.get(project_name)
        remainder_branches = self.cache.remainder.get(project_name)

        if exclude_unprotected:
            if protected_branches is not None:
                return protected_branches
        else:
            if remainder_branches is not None:
                return (protected_branches or []) + remainder_branches

        return None

    def setProjectBranches(self, project_name, exclude_unprotected, branches):
        """Set the branch names for the given project.

        :param str project_name:
            The project for the branches.
        :param bool exclude_unprotected:
            Whether this is a list of all or only protected branches.
        :param list[str] branches:
            The list of branches
        """

        with locked(self.wlock):
            with self.cache.activeContext(self.zk_context):
                if exclude_unprotected:
                    self.cache.protected[project_name] = branches
                    remainder_branches = self.cache.remainder.get(project_name)
                    if remainder_branches:
                        remainder = list(set(remainder_branches) -
                                         set(branches))
                        self.cache.remainder[project_name] = remainder
                else:
                    protected_branches = self.cache.protected.get(project_name)
                    if protected_branches:
                        remainder = list(set(branches) -
                                         set(protected_branches))
                    else:
                        remainder = branches
                    self.cache.remainder[project_name] = remainder

    def setProtected(self, project_name, branch, protected):
        """Correct the protection state of a branch.

        This may be called if a branch has changed state without us
        receiving an explicit event.
        """

        with locked(self.wlock):
            with self.cache.activeContext(self.zk_context):
                protected_branches = self.cache.protected.get(project_name)
                remainder_branches = self.cache.remainder.get(project_name)
                if protected:
                    if protected_branches is None:
                        # We've never run a protected query, so we
                        # should ignore this branch.
                        return
                    else:
                        # We have run a protected query; if we have
                        # also run an unprotected query, we need to
                        # move the branch from remainder to protected.
                        if remainder_branches and branch in remainder_branches:
                            remainder_branches.remove(branch)
                        if branch not in protected_branches:
                            protected_branches.append(branch)
                else:
                    if protected_branches and branch in protected_branches:
                        protected_branches.remove(branch)
                    if remainder_branches is None:
                        # We've never run an unprotected query, so we
                        # should ignore this branch.
                        return
                    else:
                        if branch not in remainder_branches:
                            remainder_branches.append(branch)

    @property
    def ltime(self):
        return self.cache._zstat.last_modified_transaction_id
