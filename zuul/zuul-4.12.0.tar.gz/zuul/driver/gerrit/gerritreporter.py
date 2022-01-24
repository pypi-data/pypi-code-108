# Copyright 2013 Rackspace Australia
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
import voluptuous as v

from zuul.driver.gerrit.gerritsource import GerritSource
from zuul.lib.logutil import get_annotated_logger
from zuul.model import Change
from zuul.reporter import BaseReporter


class GerritReporter(BaseReporter):
    """Sends off reports to Gerrit."""

    name = 'gerrit'
    log = logging.getLogger("zuul.GerritReporter")

    def __init__(self, driver, connection, config=None):
        super(GerritReporter, self).__init__(driver, connection, config)
        action = self.config.copy()
        self._create_comment = action.pop('comment', True)
        self._submit = action.pop('submit', False)
        self._checks_api = action.pop('checks-api', None)
        self._labels = action

    def report(self, item):
        """Send a message to gerrit."""
        log = get_annotated_logger(self.log, item.event)

        # If the source is no GerritSource we cannot report anything here.
        if not isinstance(item.change.project.source, GerritSource):
            return

        # We can only report changes, not plain branches
        if not isinstance(item.change, Change):
            return

        # For supporting several Gerrit connections we also must filter by
        # the canonical hostname.
        if item.change.project.source.connection.canonical_hostname != \
                self.connection.canonical_hostname:
            log.debug("Not reporting %s as this Gerrit reporter "
                      "is for %s and the change is from %s",
                      item, self.connection.canonical_hostname,
                      item.change.project.source.connection.canonical_hostname)
            return

        comments = self.getFileComments(item)
        if self._create_comment:
            message = self._formatItemReport(item)
        else:
            message = ''

        log.debug("Report change %s, params %s, message: %s, comments: %s",
                  item.change, self.config, message, comments)
        item.change._ref_sha = item.change.project.source.getRefSha(
            item.change.project, 'refs/heads/' + item.change.branch)

        return self.connection.review(item, message, self._submit,
                                      self._labels, self._checks_api,
                                      comments, zuul_event_id=item.event)

    def getSubmitAllowNeeds(self):
        """Get a list of code review labels that are allowed to be
        "needed" in the submit records for a change, with respect
        to this queue.  In other words, the list of review labels
        this reporter itself is likely to set before submitting.
        """
        return self._labels


def getSchema():
    gerrit_reporter = v.Any(str, v.Schema(dict))
    return gerrit_reporter
