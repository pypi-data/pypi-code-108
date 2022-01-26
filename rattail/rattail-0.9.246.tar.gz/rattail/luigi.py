# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2020 Lance Edgar
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
Luigi utilities
"""

from __future__ import unicode_literals, absolute_import

import os
import datetime
import subprocess
import sys
import logging

import luigi
import six


class OvernightTask(luigi.Task):
    """
    Base class for overnight automation tasks.
    """
    date = luigi.DateParameter()

    # TODO: subclass must define this
    filename = None

    # how long should we wait after task completes, for datasync to catch up?
    datasync_wait_minutes = None

    def output(self):
        return luigi.LocalTarget('{}/{}'.format(self.date.strftime('%Y/%m/%d'), self.filename))

    def run_command(self):
        raise NotImplementedError

    def touch_output(self):
        with self.output().open('w') as f:
            pass

    def datasync_wait(self, minutes=None, initial_delay=60):
        """
        :param int initial_delay: Number of seconds for the initial delay,
           before we actually start to wait on the queue to clear out.
        """
        if minutes is None:
            minutes = self.datasync_wait_minutes or 10

        # sometimes the datasync queue can take a moment to actually "fill up"
        # initially, so we wait a full minute to ensure that happens before we
        # start actually waiting for it to empty out again
        if initial_delay:
            subprocess.check_call(['sleep', six.text_type(initial_delay)])

        subprocess.check_call([
            'bin/rattail',
            '--config=app/cron.conf',
            'datasync',
            '--timeout={}'.format(minutes),
            'wait',
        ])

    def run(self):
        workdir = os.getcwd()
        os.chdir(sys.prefix)
        self.date_plus = self.date + datetime.timedelta(days=1)
        self.run_command()
        if self.datasync_wait_minutes:
            self.datasync_wait()
        os.chdir(workdir)
        self.touch_output()


class WarnSummaryIfProblems(logging.Filter):
    """
    Custom logging filter, to elevate the Luigi "execution summary" message to
    WARNING level, if any problems are detected for the run.  Note that this
    simply checks for the ``:)`` message to know if there were problem.
    """

    good_messages = [
        "This progress looks :) because there were no failed tasks or missing external dependencies",
        "This progress looks :) because there were no failed tasks or missing dependencies",
    ]


    def filter(self, record):
        if record.name == 'luigi-interface' and record.levelno == logging.INFO:
            if "===== Luigi Execution Summary =====" in record.msg:
                if not any([msg in record.msg for msg in self.good_messages]):
                    record.levelno = logging.WARNING
                    record.levelname = 'WARNING'
        return True
