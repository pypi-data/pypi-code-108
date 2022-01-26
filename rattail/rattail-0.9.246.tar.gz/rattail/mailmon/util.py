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
MailMon Utilities
"""

from __future__ import unicode_literals, absolute_import

import datetime

from rattail.db import api
from rattail.time import localtime, make_utc


def get_lastrun_setting(config, watcher_key):
    """
    Retrieve the "last run" setting name for the given watcher key.
    """
    return 'rattail.mailmon.{}.watcher.lastrun'.format(watcher_key)


def get_lastrun_timefmt(config):
    """
    Retrieve the "last run" time format.
    """
    return '%Y-%m-%d %H:%M:%S'


def get_lastrun(config, watcher_key, local=False, tzinfo=True, session=None):
    """
    Retrieve the "last run" time for the mailmon watcher thread
    identifed by ``watcher_key``.
    """
    # the 'last run' value is maintained as UTC
    lastrun_setting = get_lastrun_setting(config, watcher_key)
    timefmt = get_lastrun_timefmt(config)
    lastrun = api.get_setting(session, lastrun_setting)
    if lastrun:
        lastrun = datetime.datetime.strptime(lastrun, timefmt)
        if local:
            return localtime(config, lastrun, from_utc=True, tzinfo=tzinfo)
        else:
            return make_utc(lastrun, tzinfo=tzinfo)
