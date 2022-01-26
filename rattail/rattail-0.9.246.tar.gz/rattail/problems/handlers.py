# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Problem Report Handlers
"""

from __future__ import unicode_literals, absolute_import

import logging

from rattail.db import Session
from rattail.mail import send_email
from rattail.time import localtime
from rattail.util import load_object, import_module_path, progress_loop
from rattail.problems import ProblemReport, RattailProblemReport


log = logging.getLogger(__name__)


class ProblemReportHandler(object):
    """
    Base class and default implementation for problem report handlers.
    """

    def __init__(self, config, dry_run=False, progress=None):
        self.config = config
        self.dry_run = dry_run
        self.progress = progress
        self.app = self.config.get_app()
        self.enum = self.config.get_enum()

    def progress_loop(self, func, items, factory=None, **kwargs):
        factory = factory or self.progress
        return progress_loop(func, items, factory, **kwargs)

    def get_all_problem_reports(self):
        """
        Returns a simple list of all ``ProblemReport`` subclasses which are
        "available" according to config.
        """
        reports = []
        problem_modules = self.config.getlist('rattail', 'problems',
                                              default=['rattail.problems.rattail'])
        for module_path in problem_modules:
            module = import_module_path(module_path)
            for name in dir(module):
                obj = getattr(module, name)

                if (isinstance(obj, type) and
                    issubclass(obj, ProblemReport) and
                    obj not in (ProblemReport, RattailProblemReport)):

                    reports.append(obj)

        return reports

    def get_problem_reports(self, systems=None, problems=None):
        """
        Return a list of all problem reports which match the given criteria.

        :param systems: Optional list of "system keys" which a problem report
           must match, in order to be included in return value.

        :param problems: Optional list of "problem keys" which a problem report
           must match, in order to be included in return value.

        :returns: List of problem reports; may be an empty list.
        """
        all_reports = self.get_all_problem_reports()
        if not (systems or problems):
            return all_reports

        matches = []
        for report in all_reports:
            if not systems or report.system_key in systems:
                if not problems or report.problem_key in problems:
                    matches.append(report)
        return matches

    def get_problem_report(self, system_key, problem_key, **kwargs):
        """
        Return a specific problem report, identified by the
        system/problem key pair.

        :param system_key: System key, part of the identifier.

        :param problem_key: Problem key, part of the identifier.

        :returns: A specific :class:`~ProblemReport` class, if a match
           was found, otherwise ``None``.
        """
        reports = self.get_problem_reports(systems=[system_key],
                                           problems=[problem_key])
        if reports:
            if len(reports) > 1:
                raise RuntimeError("Multiple problem reports defined "
                                   "for key: {}.{}".format(
                                       system_key, problem_key))
            return reports[0]

    def organize_problem_reports(self, reports):
        """
        Returns a nested dict with the given problem reports.
        """
        organized = {}

        for report in reports:
            system = organized.setdefault(report.system_key, {})
            system[report.problem_key] = report

        return organized

    def supported_systems(self):
        """
        Returns list of keys for all systems which are supported by any of the
        available problem reports, according to config.
        """
        problem_reports = self.get_all_problem_reports()
        return sorted(set([pr.system_key for pr in problem_reports]))

    def run_problem_reports(self, reports, fix=False):
        """
        Run the given set of problem reports.

        :param fix: This flag will be passed as-is to
           :meth:`run_problem_report()`.
        """
        organized = self.organize_problem_reports(reports)
        for system_key in sorted(organized):
            system = organized[system_key]
            for problem_key in sorted(system):
                report = system[problem_key]
                self.run_problem_report(report, fix=fix)

    def run_problem_report(self, problem_report, fix=False,
                           send=True, **kwargs):
        """
        Run a specific problem report.
        """
        log.info("running problem report: %s.%s",
                 problem_report.system_key,
                 problem_report.problem_key)

        progress = kwargs.pop('progress', self.progress)
        report = problem_report(self.config,
                                dry_run=self.dry_run,
                                progress=progress)

        problems = report.find_problems(**kwargs)
        log.info("found %s problems", len(problems))
        if problems and send:
            self.send_problem_report(report, problems)
        return problems

    def get_email_key(self, report):
        if report.email_key:
            return report.email_key

        return '{}_problems_{}'.format(report.system_key,
                                       report.problem_key)

    def send_problem_report(self, report, problems):
        """
        Send out an email with details of the given problem report.
        """
        context = self.get_global_email_context()
        context = self.get_report_email_context(report, problems, **context)
        context.update({
            'report': report,
            'problems': problems,
            'app': self.app,
            'enum': self.enum,
            'render_time': self.render_time,
        })

        email_key = self.get_email_key(report)
        send_email(self.config, email_key, context,
                   default_subject=report.problem_title)

    def render_time(self, time, from_utc=True):
        """
        Render the given timestamp, localizing if necessary.
        """
        time = self.app.localtime(time, from_utc=from_utc)
        return self.app.render_datetime(time)

    def get_global_email_context(self, **kwargs):
        """
        This method can be used to add extra context for all email templates.
        """
        return kwargs

    def get_report_email_context(self, report, problems, **kwargs):
        """
        This method can be used to add extra context for a specific report's
        email template.
        """
        kwargs['system_title'] = self.get_system_title(report.system_key)
        kwargs = report.get_email_context(problems, **kwargs)
        return kwargs

    def get_system_title(self, system_key):
        """
        Should return a "display title" for the given system.
        """
        return system_key.capitalize()


def get_problem_report_handler(config, **kwargs):
    """
    Create and return the configured :class:`ProblemReportHandler` instance.
    """
    spec = config.get('rattail.problems', 'handler')
    if spec:
        factory = load_object(spec)
    else:
        factory = ProblemReportHandler
    return factory(config, **kwargs)
