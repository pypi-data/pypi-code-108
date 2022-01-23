"""
Nozomi
TimeZoneUTC Module
author: hugh@blinkybeach.com
"""
import datetime


class TimeZoneUTC(datetime.tzinfo):
    """
    UTC timezone.
    """
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return 'UTC'

    def dst(self, dt):
        return datetime.timedelta(0)


UTC = TimeZoneUTC()
