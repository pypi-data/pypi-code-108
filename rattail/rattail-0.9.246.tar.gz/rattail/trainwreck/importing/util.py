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
Trainwreck importing - shared utilities
"""

from __future__ import unicode_literals, absolute_import

import datetime

from rattail.time import localtime, make_utc


class ToOrFromTrainwreck(object):
    """
    Common base class for ToTrainwreck and FromTrainwreck base clases.
    """

    def setup(self):
        super(ToOrFromTrainwreck, self).setup()

        now = localtime(self.config)
        today = now.date()

        # start time defaults to midnight this morning, unless specified
        if not hasattr(self, 'start_time'):
            if not hasattr(self, 'start_date'):
                if self.args.start_date:
                    self.start_date = self.args.start_date
                else:
                    self.start_date = today
            start_time = datetime.datetime.combine(self.start_date, datetime.time(0))
            self.start_time = localtime(self.config, start_time)

        # end_time defaults to midnight tonight, unless specified
        if not hasattr(self, 'end_time'):
            if not hasattr(self, 'end_date'):
                if self.args.end_date:
                    self.end_date = self.args.end_date
                else:
                    self.end_date = today
            end_date = self.end_date + datetime.timedelta(days=1)
            end_time = datetime.datetime.combine(end_date, datetime.time(0))
            self.end_time = localtime(self.config, end_time)
