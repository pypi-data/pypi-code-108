#!/usr/bin/env python3
"""
Module TZTOOLS -- PLIB3 Time Zone Utilities
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains useful ``tzinfo`` subclasses,
based on those in the Python documentation for the
``datetime`` module.
"""

import os
import time as _time
from datetime import datetime, tzinfo, timedelta

from plib.stdlib.builtins import first
from plib.stdlib.proc import process_output

try:
    import dateutil
except ImportError:
    dateutil = None

try:
    import pytz
except ImportError:
    pytz = None


# TZINFO code cribbed from Python docs for datetime module

ZERO = timedelta(0)


# If dateutil or pytz are present, we use their UTC timezone object,
# otherwise we use the definition from the Python docs

if dateutil is not None:
    
    from dateutil.tz import tzutc as UTCTimezone

elif pytz is not None:
    
    UTCTimezone = lambda: pytz.utc

else:
    
    class UTCTimezone(tzinfo):
        """Fixed time zone for UTC.
        """
        
        def utcoffset(self, dt):
            return ZERO
        
        def tzname(self, dt):
            return "UTC"
        
        def dst(self, dt):
            return ZERO


if dateutil is not None:
    
    from dateutil.tz import tzlocal as LocalTimezone

else:
    
    # pytz doesn't have a "local timezone" class, so we have to
    # use the one from the Python docs
    
    STDOFFSET = timedelta(seconds=-_time.timezone)
    if _time.daylight:
        DSTOFFSET = timedelta(seconds=-_time.altzone)
    else:
        DSTOFFSET = STDOFFSET
    
    DSTDIFF = DSTOFFSET - STDOFFSET
    
    
    class LocalTimezone(tzinfo):
        """Time zone with DST support for system local time.
        """
        
        def utcoffset(self, dt):
            if self._isdst(dt):
                return DSTOFFSET
            else:
                return STDOFFSET
        
        def dst(self, dt):
            if self._isdst(dt):
                return DSTDIFF
            else:
                return ZERO
        
        def tzname(self, dt):
            return _time.tzname[self._isdst(dt)]
        
        def _isdst(self, dt):
            tt = (dt.year, dt.month, dt.day,
                dt.hour, dt.minute, dt.second,
                dt.weekday(), 0, 0)
            stamp = _time.mktime(tt)
            tt = _time.localtime(stamp)
            return tt.tm_isdst > 0


# Utility for getting local system timezone name

def _local_tzname_tzfile(tzfile="/etc/timezone"):
    # This is the best method, so try it first
    if os.path.isfile(tzfile):
        with open(tzfile, 'rU') as f:
            return f.read().strip()


def _local_tzname_etclink(linkfile="/etc/localtime", zstr="zoneinfo/"):
    # This is less desirable because the symlink may not point to a file
    # with a valid time zone name
    if os.path.islink(linkfile):
        dest = os.readlink(linkfile)
        if zstr in dest:
            return dest.split(zstr)[1]


def _iter_local_tzname_etcfile(localfile, zstr, pipetmpl, zonedirs):
    if os.path.isfile(localfile):
        for zdir in zonedirs:
            # Use old-style string formatting because {} characters are used by awk
            pipeline = pipetmpl % zdir
            result = process_output(pipeline, shell=True).strip().splitlines()
            for dest in result:
                if zstr in dest:
                    yield dest.split(zstr)[1].decode()


def _local_tzname_etcfile(localfile="/etc/localtime",
                          zstr=b"zoneinfo/",
                          pipetmpl="find /usr/%s/zoneinfo -type f"
                                   " | xargs md5sum"
                                   " | grep `md5sum /etc/localtime | awk '{print $1}'`"
                                   " | awk '{print $2}'",
                          zonedirs=("share", "lib"),
                          show_all=False):
    # This is still less desirable because the zone file may match multiple
    # files and there's no guarantee that the first match is the right one
    it = _iter_local_tzname_etcfile(localfile, zstr, pipetmpl, zonedirs)
    return list(it) if show_all else first(it)


def _iter_local_tzname_tzinfo():
    # This only works with pytz, dateutil does not provide an equivalent to common_timezones
    if pytz is not None:
        tz_local = LocalTimezone()
        dtn = datetime.now()
        dts = datetime(dtn.year, 6, 21)
        dtw = datetime(dtn.year, 12, 21)
        for tzname in pytz.common_timezones:
            tz = pytz.timezone(tzname)
            if all(tz.utcoffset(dt) == tz_local.utcoffset(dt) for dt in (dtn, dts, dtw)):
                yield tzname


def _local_tzname_tzinfo(show_all=False):
    # This is the least desirable of all because we're not matching names
    # or even all rules, just current DST rules, and again there may be multiple
    # zones that match and the first may well not be the right one
    it = _iter_local_tzname_tzinfo()
    return list(it) if show_all else first(it)


ETC_TIMEZONE = 1
ETC_LOCALTIME_LINK = 2
ETC_LOCALTIME_FILE = 3
LOCAL_TZINFO = 4

local_tz_methods = {
    ETC_TIMEZONE: _local_tzname_tzfile,
    ETC_LOCALTIME_LINK: _local_tzname_etclink,
    ETC_LOCALTIME_FILE: _local_tzname_etcfile,
    LOCAL_TZINFO: _local_tzname_tzinfo
}

show_all_methods = (
    ETC_LOCALTIME_FILE,
    LOCAL_TZINFO
)


def local_tzname(method=None, return_method=False, show_all=False):
    methods = [method] if method else sorted(local_tz_methods)
    for method in methods:
        result = local_tz_methods[method](**(
            dict(show_all=show_all) if method in show_all_methods else {}
        ))
        if result is not None:
            if return_method:
                return result, method
            return result
