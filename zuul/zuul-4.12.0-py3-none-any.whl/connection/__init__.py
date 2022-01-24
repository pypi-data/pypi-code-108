# Copyright 2014 Rackspace Australia
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

import abc
import logging

from typing import List, Optional

from zuul.lib.logutil import get_annotated_logger
from zuul.model import Project


class BaseConnection(object, metaclass=abc.ABCMeta):
    """Base class for connections.

    A connection is a shared object that sources, triggers and reporters can
    use to speak with a remote API without needing to establish a new
    connection each time or without having to authenticate each time.

    Multiple instances of the same connection may exist with different
    credentials, for example, thus allowing for different pipelines to operate
    on different Gerrit installations or post back as a different user etc.

    Connections can implement their own public methods. Required connection
    methods are validated by the {trigger, source, reporter} they are loaded
    into. For example, a trigger will likely require some kind of query method
    while a reporter may need a review method."""

    log = logging.getLogger('zuul.BaseConnection')

    def __init__(self, driver, connection_name, connection_config):
        # connection_name is the name given to this connection in zuul.ini
        # connection_config is a dictionary of config_section from zuul.ini for
        # this connection.
        # __init__ shouldn't make the actual connection in case this connection
        # isn't used in the layout.
        self.driver = driver
        self.connection_name = connection_name
        self.connection_config = connection_config
        self.sched = None

    def logEvent(self, event):
        log = get_annotated_logger(self.log, event.zuul_event_id)
        log.debug('Scheduling event from {connection}: {event}'.format(
            connection=self.connection_name,
            event=event))
        try:
            if self.sched.statsd:
                self.sched.statsd.incr(
                    'zuul.event.{driver}.{event}'.format(
                        driver=self.driver.name, event=event.type))
                self.sched.statsd.incr(
                    'zuul.event.{driver}.{connection}.{event}'.format(
                        driver=self.driver.name,
                        connection=self.connection_name,
                        event=event.type))
        except Exception:
            self.log.exception("Exception reporting event stats")

    def onLoad(self, zk_client):
        pass

    def onStop(self):
        pass

    def registerScheduler(self, sched) -> None:
        self.sched = sched

    def cleanupCache(self):
        """Clean up the connection cache.

        This allows a connection to perform periodic cleanup actions of
        the cache, e.g. garbage collection.
        """
        pass

    def maintainCache(self, relevant, max_age):
        """Remove stale changes from the cache.

        This lets the user supply a list of change cache keys that are
        still in use.  Anything in our cache that isn't in the supplied
        list and is older than the given max. age (in seconds) should
        be safe to remove from the cache."""
        pass

    def getWebController(self, zuul_web):
        """Return a cherrypy web controller to register with zuul-web.

        :param zuul.web.ZuulWeb zuul_web:
            Zuul Web instance.
        :returns: A `zuul.web.handler.BaseWebController` instance.
        """
        return None

    def getEventQueue(self):
        """Return the event queue for this connection.

        :returns: A `zuul.zk.event_queues.ConnectionEventQueue` instance
                  or None.
        """
        return None

    def validateWebConfig(self, config, connections):
        """Validate web config.

        If there is a fatal error, the method should raise an exception.

        :param config:
           The parsed config object.
        :param zuul.lib.connections.ConnectionRegistry connections:
           Registry of all configured connections.
        """
        return False

    def toDict(self):
        """Return public information about the connection
        """
        return {
            "name": self.connection_name,
            "driver": self.driver.name,
        }


class ZKBranchCacheMixin:
    # Expected to be defined by the connection and to be an instance
    # of BranchCache
    _branch_cache = None
    read_only = False

    @abc.abstractmethod
    def isBranchProtected(self, project_name: str, branch_name: str,
                          zuul_event_id) -> Optional[bool]:
        """Return if the branch is protected or None if the branch is unknown.

        :param str project_name:
            The name of the project.
        :param str branch_name:
            The name of the branch.
        :param zuul_event_id:
            Unique id associated to the handled event.
        """
        pass

    @abc.abstractmethod
    def _fetchProjectBranches(self, project: Project,
                              exclude_unprotected: bool) -> List[str]:
        pass

    def clearConnectionCacheOnBranchEvent(self, event):
        """Update event and clear connection cache if needed.

        This checks whether the event created or deleted a branch so
        that Zuul may know to perform a reconfiguration on the
        project. Drivers must call this method when a branch event is
        received.

        :param event:
            The event, inherit from `zuul.model.TriggerEvent` class.
        """
        if event.oldrev == '0' * 40:
            event.branch_created = True
        elif event.newrev == '0' * 40:
            event.branch_deleted = True
        else:
            event.branch_updated = True

        project = self.source.getProject(event.project_name)
        if event.branch:
            if event.branch_deleted:
                # We currently cannot determine if a deleted branch was
                # protected so we need to assume it was. GitHub/GitLab don't
                # allow deletion of protected branches but we don't get a
                # notification about branch protection settings. Thus we don't
                # know if branch protection has been disabled before deletion
                # of the branch.
                # FIXME(tobiash): Find a way to handle that case
                self.updateProjectBranches(project)
            elif event.branch_created:
                # In GitHub, a new branch never can be protected
                # because that needs to be configured after it has
                # been created.  Other drivers could optimize this,
                # but for the moment, implement the lowest common
                # denominator and clear the cache so that we query.
                self.updateProjectBranches(project)
            event.branch_cache_ltime = self._branch_cache.ltime
        return event

    def updateProjectBranches(self, project):
        """Update the branch cache for the project.

        :param zuul.model.Project project:
            The project for which the branches are returned.
        """
        # Figure out which queries we have a cache for
        protected_branches = self._branch_cache.getProjectBranches(
            project.name, True)
        all_branches = self._branch_cache.getProjectBranches(
            project.name, False)

        # Update them if we have them
        if protected_branches is not None:
            protected_branches = self._fetchProjectBranches(
                project, True)
            self._branch_cache.setProjectBranches(
                project.name, True, protected_branches)

        if all_branches is not None:
            all_branches = self._fetchProjectBranches(project, False)
            self._branch_cache.setProjectBranches(
                project.name, False, all_branches)
        self.log.info("Got branches for %s" % project.name)

    def getProjectBranches(self, project, tenant, min_ltime=-1):
        """Get the branch names for the given project.

        :param zuul.model.Project project:
            The project for which the branches are returned.
        :param zuul.model.Tenant tenant:
            The related tenant.
        :param int min_ltime:
            The minimum ltime to determine if we need to refresh the cache.

        :returns: The list of branch names.
        """
        exclude_unprotected = tenant.getExcludeUnprotectedBranches(project)
        if self._branch_cache:
            branches = self._branch_cache.getProjectBranches(
                project.name, exclude_unprotected, min_ltime)
        else:
            # Handle the case where tenant validation doesn't use the cache
            branches = None

        if branches is not None:
            return sorted(branches)

        if self.read_only:
            raise RuntimeError(
                "Will not fetch project branches as read-only is set")

        # We need to perform a query
        branches = self._fetchProjectBranches(project, exclude_unprotected)
        self.log.info("Got branches for %s" % project.name)

        if self._branch_cache:
            self._branch_cache.setProjectBranches(
                project.name, exclude_unprotected, branches)

        return sorted(branches)

    def checkBranchCache(self, project_name: str, event,
                         protected: bool = None) -> None:
        """Clear the cache for a project when a branch event is processed

        This method must be called when a branch event is processed: if the
        event references a branch and the unprotected branches are excluded,
        the branch protection status could have been changed.

        :params str project_name:
            The project name.
        :params event:
            The event, inherit from `zuul.model.TriggerEvent` class.
        :params protected:
            If defined the caller already knows if the branch is protected
            so the query can be skipped.
        """
        if protected is None:
            protected = self.isBranchProtected(project_name, event.branch,
                                               zuul_event_id=event)
        if protected is not None:

            # If the branch appears in the exclude_unprotected cache but
            # is unprotected, clear the exclude cache.

            # If the branch does not appear in the exclude_unprotected
            # cache but is protected, clear the exclude cache.

            # All branches should always appear in the include_unprotected
            # cache, so we never clear it.

            branches = self._branch_cache.getProjectBranches(
                project_name, True)
            if not branches:
                branches = []

            update = False
            if (event.branch in branches) and (not protected):
                update = True
            if (event.branch not in branches) and (protected):
                update = True
            if update:
                self.log.info("Project %s branch %s protected state "
                              "changed to %s",
                              project_name, event.branch, protected)
                self._branch_cache.setProtected(project_name, event.branch,
                                                protected)
                event.branch_cache_ltime = self._branch_cache.ltime

            event.branch_protected = protected
        else:
            # This can happen if the branch was deleted in GitHub/GitLab.
            # In this case we assume that the branch COULD have
            # been protected before. The cache update is handled by
            # the push event, so we don't touch the cache here
            # again.
            event.branch_protected = True


class ZKChangeCacheMixin:
    # Expected to be defined by the connection and to be an instance
    # that implements the AbstractChangeCache API.
    _change_cache = None

    def cleanupCache(self):
        self._change_cache.cleanup()

    def maintainCache(self, relevant, max_age):
        self._change_cache.prune(relevant, max_age)

    def updateChangeAttributes(self, change, **attrs):
        def _update_attrs(c):
            for name, value in attrs.items():
                setattr(c, name, value)
        self._change_cache.updateChangeWithRetry(change.cache_stat.key,
                                                 change, _update_attrs)

    def getChangeByKey(self, key):
        return self._change_cache.get(key)
