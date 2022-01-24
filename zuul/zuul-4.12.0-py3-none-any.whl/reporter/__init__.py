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
from zuul.lib.config import get_default


class BaseReporter(object, metaclass=abc.ABCMeta):
    """Base class for reporters.

    Defines the exact public methods that must be supplied.
    """

    log = logging.getLogger("zuul.reporter.BaseReporter")

    def __init__(self, driver, connection, config=None):
        self.driver = driver
        self.connection = connection
        self.config = config or {}
        self._action = None

    def setAction(self, action):
        self._action = action

    @abc.abstractmethod
    def report(self, item):
        """Send the compiled report message."""

    def getSubmitAllowNeeds(self):
        """Get a list of code review labels that are allowed to be
        "needed" in the submit records for a change, with respect
        to this queue.  In other words, the list of review labels
        this reporter itself is likely to set before submitting.
        """
        return []

    def postConfig(self):
        """Run tasks after configuration is reloaded"""

    def addConfigurationErrorComments(self, item, comments):
        """Add file comments for configuration errors.

        Updates the comments dictionary with additional file comments
        for any relevant configuration errors for this item's change.

        :arg QueueItem item: The queue item
        :arg dict comments: a file comments dictionary

        """

        for err in item.getConfigErrors():
            context = err.key.context
            mark = err.key.mark
            if not (context and mark and err.short_error):
                continue
            if context.project_canonical_name != \
                    item.change.project.canonical_name:
                continue
            if not hasattr(item.change, 'branch'):
                continue
            if context.branch != item.change.branch:
                continue
            if context.path not in item.change.files:
                continue
            existing_comments = comments.setdefault(context.path, [])
            existing_comments.append(dict(line=mark.end_line,
                                          message=err.short_error,
                                          range=dict(
                                              start_line=mark.line + 1,
                                              start_character=mark.column,
                                              end_line=mark.end_line,
                                              end_character=mark.end_column)))

    def _getFileComments(self, item):
        """Get the file comments from the zuul_return value"""
        ret = {}
        for build in item.current_build_set.getBuilds():
            fc = build.result_data.get("zuul", {}).get("file_comments")
            if not fc:
                continue
            for fn, comments in fc.items():
                existing_comments = ret.setdefault(fn, [])
                existing_comments.extend(comments)
        self.addConfigurationErrorComments(item, ret)
        return ret

    def getFileComments(self, item):
        comments = self._getFileComments(item)
        self.filterComments(item, comments)
        return comments

    def filterComments(self, item, comments):
        """Filter comments for files in change

        Remove any comments for files which do not appear in the
        item's change.  Leave warning messages if this happens.

        :arg QueueItem item: The queue item
        :arg dict comments: a file comments dictionary (modified in place)
        """

        for fn in list(comments.keys()):
            if fn not in item.change.files:
                del comments[fn]
                item.warning("Comments left for invalid file %s" % (fn,))

    def _getFormatter(self, action):
        format_methods = {
            'enqueue': self._formatItemReportEnqueue,
            'start': self._formatItemReportStart,
            'success': self._formatItemReportSuccess,
            'failure': self._formatItemReportFailure,
            'merge-failure': self._formatItemReportMergeFailure,
            'no-jobs': self._formatItemReportNoJobs,
            'disabled': self._formatItemReportDisabled,
            'dequeue': self._formatItemReportDequeue,
        }
        return format_methods[action]

    def _formatItemReport(self, item, with_jobs=True, action=None):
        """Format a report from the given items. Usually to provide results to
        a reporter taking free-form text."""
        action = action or self._action
        ret = self._getFormatter(action)(item, with_jobs)

        if item.current_build_set.warning_messages:
            warning = '\n  '.join(item.current_build_set.warning_messages)
            ret += '\nWarning:\n  ' + warning + '\n'

        if item.current_build_set.debug_messages:
            debug = '\n  '.join(item.current_build_set.debug_messages)
            ret += '\nDebug information:\n  ' + debug + '\n'

        if item.pipeline.footer_message:
            ret += '\n' + item.pipeline.footer_message

        return ret

    def _formatItemReportEnqueue(self, item, with_jobs=True):
        status_url = self.connection.sched.globals.web_status_url
        if status_url:
            status_url = item.formatUrlPattern(status_url)

        return item.pipeline.enqueue_message.format(
            pipeline=item.pipeline.getSafeAttributes(),
            change=item.change.getSafeAttributes(),
            status_url=status_url)

    def _formatItemReportStart(self, item, with_jobs=True):
        status_url = self.connection.sched.globals.web_status_url
        if status_url:
            status_url = item.formatUrlPattern(status_url)

        return item.pipeline.start_message.format(
            pipeline=item.pipeline.getSafeAttributes(),
            change=item.change.getSafeAttributes(),
            status_url=status_url)

    def _formatItemReportSuccess(self, item, with_jobs=True):
        msg = item.pipeline.success_message
        if with_jobs:
            msg += '\n\n' + self._formatItemReportJobs(item)
        return msg

    def _formatItemReportFailure(self, item, with_jobs=True):
        if item.cannotMergeBundle():
            msg = 'This change is part of a bundle that failed to merge.\n'
        elif item.dequeued_needing_change:
            msg = 'This change depends on a change that failed to merge.\n'
        elif item.isBundleFailing():
            msg = 'This change is part of a bundle that failed.\n'
            if with_jobs:
                msg = '{}\n\n{}'.format(msg, self._formatItemReportJobs(item))
            msg = "{}\n\n{}".format(
                msg, self._formatItemReportOtherBundleItems(item))
        elif item.didMergerFail():
            msg = item.pipeline.merge_failure_message
        elif item.getConfigErrors():
            msg = str(item.getConfigErrors()[0].error)
        else:
            msg = item.pipeline.failure_message
            if with_jobs:
                msg += '\n\n' + self._formatItemReportJobs(item)
        return msg

    def _formatItemReportMergeFailure(self, item, with_jobs=True):
        return item.pipeline.merge_failure_message

    def _formatItemReportNoJobs(self, item, with_jobs=True):
        status_url = get_default(self.connection.sched.config,
                                 'web', 'status_url', '')
        if status_url:
            status_url = item.formatUrlPattern(status_url)

        return item.pipeline.no_jobs_message.format(
            pipeline=item.pipeline.getSafeAttributes(),
            change=item.change.getSafeAttributes(),
            status_url=status_url)

    def _formatItemReportDisabled(self, item, with_jobs=True):
        if item.current_build_set.result == 'SUCCESS':
            return self._formatItemReportSuccess(item)
        elif item.current_build_set.result == 'FAILURE':
            return self._formatItemReportFailure(item)
        else:
            return self._formatItemReport(item)

    def _formatItemReportDequeue(self, item, with_jobs=True):
        msg = item.pipeline.dequeue_message
        if with_jobs:
            msg += '\n\n' + self._formatItemReportJobs(item)
        return msg

    def _formatItemReportOtherBundleItems(self, item):
        related_changes = item.pipeline.manager.resolveChangeReferences(
            item.change.needs_changes)
        return "Related changes:\n{}".format("\n".join(
            c.url for c in related_changes if c is not item.change))

    def _getItemReportJobsFields(self, item):
        # Extract the report elements from an item
        config = self.connection.sched.config
        jobs_fields = []
        for job in item.getJobs():
            build = item.current_build_set.getBuild(job.name)
            (result, url) = item.formatJobResult(job)
            if not job.voting:
                voting = ' (non-voting)'
            else:
                voting = ''

            if config and config.has_option(
                'zuul', 'report_times'):
                report_times = config.getboolean(
                    'zuul', 'report_times')
            else:
                report_times = True

            if report_times and build.end_time and build.start_time:
                dt = int(build.end_time - build.start_time)
                m, s = divmod(dt, 60)
                h, m = divmod(m, 60)
                if h:
                    elapsed = ' in %dh %02dm %02ds' % (h, m, s)
                elif m:
                    elapsed = ' in %dm %02ds' % (m, s)
                else:
                    elapsed = ' in %ds' % (s)
            else:
                elapsed = ''
            if build.error_detail:
                error = ' ' + build.error_detail
            else:
                error = ''
            name = job.name + ' '
            # TODO(mordred) The gerrit consumption interface depends on
            # something existing in the url field and don't have a great
            # behavior defined for url being none/missing. Put name into
            # the url field to match old behavior until we can deal with
            # the gerrit-side piece as well
            url = url or job.name
            # Pass user defined success_message deciding the build result
            # during result formatting
            success_message = job.success_message
            jobs_fields.append(
                (name, url, result, error, elapsed, voting, success_message))
        return jobs_fields

    def _formatItemReportJobs(self, item):
        # Return the list of jobs portion of the report
        ret = ''
        jobs_fields = self._getItemReportJobsFields(item)
        for job_fields in jobs_fields:
            ret += '- %s%s : %s%s%s%s\n' % job_fields[:6]
        return ret
