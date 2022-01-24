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

import time
import logging
import voluptuous as v

from zuul.reporter import BaseReporter
from zuul.model import MERGER_MERGE_RESOLVE, MERGER_MERGE, MERGER_MAP, \
    MERGER_SQUASH_MERGE
from zuul.lib.logutil import get_annotated_logger
from zuul.driver.gitlab.gitlabsource import GitlabSource
from zuul.exceptions import MergeFailure


class GitlabReporter(BaseReporter):
    """Sends off reports to Gitlab."""

    name = 'gitlab'
    log = logging.getLogger("zuul.GitlabReporter")

    # Merge modes supported by gitlab
    merge_modes = {
        MERGER_MERGE: 'merge',
        MERGER_MERGE_RESOLVE: 'merge',
        MERGER_SQUASH_MERGE: 'squash'
    }

    def __init__(self, driver, connection, pipeline, config=None):
        super(GitlabReporter, self).__init__(driver, connection, config)
        self._create_comment = self.config.get('comment', True)
        self._approval = self.config.get('approval', None)
        self._merge = self.config.get('merge', False)

    def report(self, item):
        """Report on an event."""
        if not isinstance(item.change.project.source, GitlabSource):
            return

        if item.change.project.source.connection.canonical_hostname != \
                self.connection.canonical_hostname:
            return

        if hasattr(item.change, 'number'):
            if self._create_comment:
                self.addMRComment(item)
            if self._approval is not None:
                self.setApproval(item)
            if self._merge:
                self.mergeMR(item)
                if not item.change.is_merged:
                    msg = self._formatItemReportMergeFailure(item)
                    self.addMRComment(item, msg)

    def addMRComment(self, item, comment=None):
        log = get_annotated_logger(self.log, item.event)
        message = comment or self._formatItemReport(item)
        project = item.change.project.name
        mr_number = item.change.number
        log.debug('Reporting change %s, params %s, message: %s',
                  item.change, self.config, message)
        self.connection.commentMR(project, mr_number, message,
                                  event=item.event)

    def setApproval(self, item):
        log = get_annotated_logger(self.log, item.event)
        project = item.change.project.name
        mr_number = item.change.number
        patchset = item.change.patchset
        log.debug('Reporting change %s, params %s, approval: %s',
                  item.change, self.config, self._approval)
        self.connection.approveMR(project, mr_number, patchset,
                                  self._approval, event=item.event)

    def mergeMR(self, item):
        project = item.change.project.name
        mr_number = item.change.number

        merge_mode = item.current_build_set.getMergeMode()

        if merge_mode not in self.merge_modes:
            mode = [x[0] for x in MERGER_MAP.items() if x[1] == merge_mode][0]
            self.log.warning('Merge mode %s not supported by Gitlab', mode)
            raise MergeFailure('Merge mode %s not supported by Gitlab' % mode)

        merge_mode = self.merge_modes[merge_mode]

        for i in [1, 2]:
            try:
                self.connection.mergeMR(project, mr_number, merge_mode)
                item.change.is_merged = True
                return
            except MergeFailure:
                self.log.exception(
                    'Merge attempt of change %s  %s/2 failed.' %
                    (item.change, i), exc_info=True)
                if i == 1:
                    time.sleep(2)
        self.log.warning(
            'Merge of change %s failed after 2 attempts, giving up' %
            item.change)

    def getSubmitAllowNeeds(self):
        return []


def getSchema():
    gitlab_reporter = v.Schema({
        'comment': bool,
        'approval': bool,
        'merge': bool,
    })
    return gitlab_reporter
