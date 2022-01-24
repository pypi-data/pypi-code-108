# Copyright 2011 OpenStack, LLC.
# Copyright 2012 Hewlett-Packard Development Company, L.P.
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

import os
import git
import time
import logging
import urllib

from zuul.connection import BaseConnection, ZKChangeCacheMixin
from zuul.driver.git.gitmodel import GitTriggerEvent
from zuul.driver.git.gitwatcher import GitWatcher
from zuul.model import Ref, Branch
from zuul.zk.change_cache import (
    AbstractChangeCache,
    ChangeKey,
    ConcurrentUpdateError,
)


class GitChangeCache(AbstractChangeCache):
    log = logging.getLogger("zuul.driver.GitChangeCache")

    CHANGE_TYPE_MAP = {
        "Ref": Ref,
        "Branch": Branch,
    }


class GitConnection(ZKChangeCacheMixin, BaseConnection):
    driver_name = 'git'
    log = logging.getLogger("zuul.connection.git")

    def __init__(self, driver, connection_name, connection_config):
        super(GitConnection, self).__init__(driver, connection_name,
                                            connection_config)
        if 'baseurl' not in self.connection_config:
            raise Exception('baseurl is required for git connections in '
                            '%s' % self.connection_name)
        self.watcher_thread = None
        self.baseurl = self.connection_config.get('baseurl')
        self.poll_timeout = float(
            self.connection_config.get('poll_delay', 3600 * 2))
        self.canonical_hostname = self.connection_config.get(
            'canonical_hostname')
        if not self.canonical_hostname:
            r = urllib.parse.urlparse(self.baseurl)
            if r.hostname:
                self.canonical_hostname = r.hostname
            else:
                self.canonical_hostname = 'localhost'
        self.projects = {}
        self.source = driver.getSource(self)

    def toDict(self):
        d = super().toDict()
        d.update({
            "baseurl": self.baseurl,
            "canonical_hostname": self.canonical_hostname,
        })
        return d

    def getProject(self, name):
        return self.projects.get(name)

    def addProject(self, project):
        self.projects[project.name] = project

    def getChangeFilesUpdated(self, project_name, branch, tosha):
        job = self.sched.merger.getFilesChanges(
            self.connection_name, project_name, branch, tosha,
            needs_result=True)
        self.log.debug("Waiting for fileschanges job %s" % job)
        job.wait()
        if not job.updated:
            raise Exception("Fileschanges job %s failed" % job)
        self.log.debug("Fileschanges job %s got changes on files %s" %
                       (job, job.files))
        return job.files

    def lsRemote(self, project):
        refs = {}
        client = git.cmd.Git()
        output = client.ls_remote(
            "--heads", "--tags",
            os.path.join(self.baseurl, project))
        for line in output.splitlines():
            sha, ref = line.split('\t')
            if ref.startswith('refs/'):
                refs[ref] = sha
        return refs

    def getChange(self, event, refresh=False):
        key = ChangeKey(self.connection_name, event.project_name,
                        'Ref', event.ref, event.newrev)
        change = self._change_cache.get(key)
        if change:
            return change

        if event.ref and event.ref.startswith('refs/heads/'):
            branch = event.ref[len('refs/heads/'):]
            project = self.getProject(event.project_name)
            change = Branch(project)
            change.branch = branch
            change.ref = event.ref
            change.oldrev = event.oldrev
            change.newrev = event.newrev
            change.url = ""
            change.files = self.getChangeFilesUpdated(
                event.project_name, change.branch, event.oldrev)
        elif event.ref:
            # catch-all ref (ie, not a branch or head)
            project = self.getProject(event.project_name)
            change = Ref(project)
            change.ref = event.ref
            change.oldrev = event.oldrev
            change.newrev = event.newrev
            change.url = ""
        else:
            self.log.warning("Unable to get change for %s", event)
            return None

        try:
            self._change_cache.set(key, change)
        except ConcurrentUpdateError:
            change = self._change_cache.get(key)
        return change

    def getProjectBranches(self, project, tenant, min_ltime=-1):
        refs = self.lsRemote(project.name)
        branches = [ref[len('refs/heads/'):] for ref in
                    refs if ref.startswith('refs/heads/')]
        return branches

    def getGitUrl(self, project):
        return os.path.join(self.baseurl, project.name)

    def watcherCallback(self, data):
        event = GitTriggerEvent()
        event.connection_name = self.connection_name
        event.type = 'ref-updated'
        event.timestamp = time.time()
        event.project_hostname = self.canonical_hostname
        event.project_name = data['project']
        for attr in ('ref', 'oldrev', 'newrev', 'branch_created',
                     'branch_deleted', 'branch_updated'):
            if attr in data:
                setattr(event, attr, data[attr])

        # Force changes cache update before passing
        # the event to the scheduler
        self.getChange(event)
        self.logEvent(event)
        # Pass the event to the scheduler
        self.sched.addTriggerEvent(self.driver_name, event)

    def onLoad(self, zk_client):
        self.log.debug("Creating Zookeeper change cache")
        self._change_cache = GitChangeCache(zk_client, self)

        # If the connection was not loaded by a scheduler, but by e.g.
        # zuul-web, we want to stop here.
        if not self.sched:
            return

        self.log.debug("Starting Git Watcher")
        self._start_watcher_thread()

    def onStop(self):
        self.log.debug("Stopping Git Watcher")
        self._stop_watcher_thread()

    def _stop_watcher_thread(self):
        if self.watcher_thread:
            self.watcher_thread.stop()
            self.watcher_thread.join()

    def _start_watcher_thread(self):
        self.watcher_thread = GitWatcher(
            self,
            self.baseurl,
            self.poll_timeout,
            self.watcherCallback)
        self.watcher_thread.start()
