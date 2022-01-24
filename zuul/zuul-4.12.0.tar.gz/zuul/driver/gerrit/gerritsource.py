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

import re
import urllib
import logging
import voluptuous as vs
from urllib.parse import urlparse
from zuul.source import BaseSource
from zuul.model import Project
from zuul.driver.gerrit.gerritmodel import GerritRefFilter
from zuul.driver.util import scalar_or_list, to_list
from zuul.lib.dependson import find_dependency_headers


class GerritSource(BaseSource):
    name = 'gerrit'
    log = logging.getLogger("zuul.source.Gerrit")

    def __init__(self, driver, connection, config=None):
        hostname = connection.canonical_hostname
        super(GerritSource, self).__init__(driver, connection,
                                           hostname, config)
        prefix_ui = urlparse(self.connection.baseurl).path
        if prefix_ui:
            prefix_ui = prefix_ui.lstrip('/').rstrip('/')
            prefix_ui += '/'

        self.change_re = re.compile(
            r"/%s(\#\/c\/|c\/.*\/\+\/)?(\d+)[\w]*" % prefix_ui)

    def getRefSha(self, project, ref):
        return self.connection.getRefSha(project, ref)

    def isMerged(self, change, head=None):
        return self.connection.isMerged(change, head)

    def canMerge(self, change, allow_needs, event=None, allow_refresh=False):
        # Gerrit changes have no volatile data that cannot be updated via
        # events and thus needs not to act on allow_refresh.
        return self.connection.canMerge(change, allow_needs, event=event)

    def postConfig(self):
        pass

    def getChange(self, event, refresh=False):
        return self.connection.getChange(event, refresh)

    def getChangeByURL(self, url, event):
        try:
            parsed = urllib.parse.urlparse(url)
        except ValueError:
            return None
        path = parsed.path
        if parsed.fragment:
            path += '#' + parsed.fragment
        m = self.change_re.match(path)
        if not m:
            return None
        try:
            change_no = int(m.group(2))
        except ValueError:
            return None
        query = "change:%s" % (change_no,)
        results = self.connection.simpleQuery(query, event=event)
        if not results:
            return None
        change = self.connection._getChange(
            results[0].number, results[0].current_patchset,
            event=event)
        return change

    def getChangeByKey(self, key):
        return self.connection.getChangeByKey(key)

    def getChangesDependingOn(self, change, projects, tenant):
        changes = []
        if not change.uris:
            return changes
        queries = set()
        for uri in change.uris:
            queries.add('message:{Depends-On: %s}' % uri)
        query = '(' + ' OR '.join(queries) + ')'
        results = self.connection.simpleQuery(query)
        seen = set()
        for result in results:
            for match in find_dependency_headers(result.message):
                found = False
                for uri in change.uris:
                    if uri in match:
                        found = True
                        break
                if not found:
                    continue
                key = (result.number, result.current_patchset)
                if key in seen:
                    continue
                seen.add(key)
                change = self.connection._getChange(
                    result.number, result.current_patchset)
                changes.append(change)
        return changes

    def getCachedChanges(self):
        yield from self.connection._change_cache

    def getProject(self, name):
        p = self.connection.getProject(name)
        if not p:
            p = Project(name, self)
            self.connection.addProject(p)
        return p

    def getProjectOpenChanges(self, project):
        return self.connection.getProjectOpenChanges(project)

    def getProjectBranches(self, project, tenant, min_ltime=-1):
        return self.connection.getProjectBranches(project, tenant, min_ltime)

    def getProjectBranchCacheLtime(self):
        return self.connection._branch_cache.ltime

    def getGitUrl(self, project):
        return self.connection.getGitUrl(project)

    def _getGitwebUrl(self, project, sha=None):
        return self.connection._getGitwebUrl(project, sha)

    def getRequireFilters(self, config):
        f = GerritRefFilter(
            connection_name=self.connection.connection_name,
            open=config.get('open'),
            current_patchset=config.get('current-patchset'),
            statuses=to_list(config.get('status')),
            required_approvals=to_list(config.get('approval')),
        )
        return [f]

    def getRejectFilters(self, config):
        f = GerritRefFilter(
            connection_name=self.connection.connection_name,
            reject_approvals=to_list(config.get('approval')),
        )
        return [f]

    def getRefForChange(self, change):
        partial = str(change).zfill(2)[-2:]
        return "refs/changes/%s/%s/.*" % (partial, change)

    def setChangeAttributes(self, change, **attrs):
        return self.connection.updateChangeAttributes(change, **attrs)


approval = vs.Schema({'username': str,
                      'email': str,
                      'older-than': str,
                      'newer-than': str,
                      }, extra=vs.ALLOW_EXTRA)


def getRequireSchema():
    require = {'approval': scalar_or_list(approval),
               'open': bool,
               'current-patchset': bool,
               'status': scalar_or_list(str)}

    return require


def getRejectSchema():
    reject = {'approval': scalar_or_list(approval)}

    return reject
