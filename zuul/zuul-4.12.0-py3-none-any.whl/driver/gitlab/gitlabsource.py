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

import re
import logging
import urllib

from zuul.model import Project
from zuul.source import BaseSource

from zuul.driver.gitlab.gitlabmodel import GitlabRefFilter
from zuul.driver.util import scalar_or_list, to_list


class GitlabSource(BaseSource):
    name = 'gitlab'
    log = logging.getLogger("zuul.source.GitlabSource")

    def __init__(self, driver, connection, config=None):
        hostname = connection.canonical_hostname
        super(GitlabSource, self).__init__(driver, connection,
                                           hostname, config)
        self.change_re = re.compile(r"/(.*?)/(?:-/)?merge_requests/(\d+)")

    def getRefSha(self, project, ref):
        """Return a sha for a given project ref."""
        raise NotImplementedError()

    def waitForRefSha(self, project, ref, old_sha=''):
        """Block until a ref shows up in a given project."""
        raise NotImplementedError()

    def isMerged(self, change, head=None):
        """Determine if change is merge."""
        if not change.number:
            return True
        return change.is_merged

    def canMerge(self, change, allow_needs, event=None, allow_refresh=False):
        """Determine if change can merge."""
        if not change.number:
            return True
        return self.connection.canMerge(change, allow_needs, event=event)

    def postConfig(self):
        """Called after configuration has been processed."""
        raise NotImplementedError()

    def getChange(self, event, refresh=False):
        return self.connection.getChange(event, refresh)

    def getChangeByURL(self, url, event):
        try:
            parsed = urllib.parse.urlparse(url)
        except ValueError:
            return None
        m = self.change_re.match(parsed.path)
        if not m:
            return None
        project_name = m.group(1)
        try:
            num = int(m.group(2))
        except ValueError:
            return None
        mr = self.connection.getMR(project_name, num)
        if not mr:
            return None
        project = self.getProject(project_name)
        change = self.connection._getChange(
            project, num, mr['sha'], url=url,
            event=event)
        return change

    def getChangeByKey(self, key):
        return self.connection.getChangeByKey(key)

    def getChangesDependingOn(self, change, projects, tenant):
        return self.connection.getChangesDependingOn(
            change, projects, tenant)

    def getCachedChanges(self):
        yield from self.connection._change_cache

    def getProject(self, name):
        p = self.connection.getProject(name)
        if not p:
            p = Project(name, self)
            self.connection.addProject(p)
        return p

    def getProjectBranches(self, project, tenant, min_ltime=-1):
        return self.connection.getProjectBranches(project, tenant, min_ltime)

    def getProjectBranchCacheLtime(self):
        return self.connection._branch_cache.ltime

    def getProjectOpenChanges(self, project):
        """Get the open changes for a project."""
        raise NotImplementedError()

    def updateChange(self, change, history=None):
        """Update information for a change."""
        raise NotImplementedError()

    def getGitUrl(self, project):
        """Get the git url for a project."""
        return self.connection.getGitUrl(project)

    def getGitwebUrl(self, project, sha=None):
        """Get the git-web url for a project."""
        raise NotImplementedError()

    def getRequireFilters(self, config):
        f = GitlabRefFilter(
            connection_name=self.connection.connection_name,
            open=config.get('open'),
            merged=config.get('merged'),
            approved=config.get('approved'),
            labels=to_list(config.get('labels')),
        )
        return [f]

    def getRejectFilters(self, config):
        raise NotImplementedError()

    def getRefForChange(self, change):
        raise NotImplementedError()

    def setChangeAttributes(self, change, **attrs):
        return self.connection.updateChangeAttributes(change, **attrs)


# Require model
def getRequireSchema():
    require = {
        'open': bool,
        'merged': bool,
        'approved': bool,
        'labels': scalar_or_list(str)
    }
    return require


def getRejectSchema():
    reject = {}
    return reject
