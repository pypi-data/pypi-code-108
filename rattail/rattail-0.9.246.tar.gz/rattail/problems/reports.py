# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
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
Problem Reports Framework
"""

from __future__ import unicode_literals, absolute_import

from rattail.util import progress_loop
from rattail.db import cache


class ProblemReport(object):
    """
    Base class for all problem reports.

    A "problem report" will generally contain logic which looks for problems of
    some kind or another, within the data of a given system.  It may or may not
    be able to "fix" some of these problems.  In either case it is expected to
    be able to generate and send an email report with the details.
    """
    system_key = None
    problem_key = None
    problem_title = None
    email_key = None

    def __init__(self, config, dry_run=False, progress=None):
        self.config = config
        self.dry_run = dry_run
        self.progress = progress
        self.app = self.config.get_app()
        self.model = self.config.get_model()
        self.enum = self.config.get_enum()

    def progress_loop(self, func, items, factory=None, **kwargs):
        factory = factory or self.progress
        return progress_loop(func, items, factory, **kwargs)

    def cache_model(self, session, model, **kwargs):
        """
        Convenience method which invokes
        :func:`~rattail.db.cache.cache_model()` with the given model and
        keyword arguments.  This method will provide the ``progress`` parameter
        by default.
        """
        kwargs.setdefault('progress', self.progress)
        return cache.cache_model(session, model, **kwargs)

    def find_problems(self, **kwargs):
        """
        Find all problems for which this report is responsible.  This should
        always return a list, although no constraint is made on what the
        elements must be.
        """
        return []

    def get_email_context(self, problems, **kwargs):
        """
        This method can be used to add extra context for a specific report's
        email template.
        """
        return kwargs
