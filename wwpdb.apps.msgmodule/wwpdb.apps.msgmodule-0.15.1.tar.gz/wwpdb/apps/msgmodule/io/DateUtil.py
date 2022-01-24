##
#
# File:    DateUtil.py
# Author:  E. Peisach
# Date:    17-Nov-2018
# Version: 0.001
# Updates:
"""
Class to manipulate dates for display purposes
"""

__docformat__ = "restructuredtext en"
__author__ = "Ezra Peisach"
__email__ = "ezra.peisach@rcsb.org"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"

import datetime


class DateUtil(object):
    def __init__(self):
        pass

    @staticmethod
    def date_to_display(date):
        """Converts incoming dateIn from ISO 8601 YYYY-MM-DD to Month number, year
        If dateIn is '.' or '?' returns [UNKNOWN]. If date cannot be parsed, returns date.
        This should be picked up by dictionary checks.
        """

        ret = "[UNKNOWN]"
        if date not in [".", "?"]:
            try:
                dt = datetime.datetime.strptime(date, "%Y-%m-%d")
                ret = dt.strftime("%-d %B %Y")
            except ValueError:
                ret = date

        return ret

    @staticmethod
    def datetime_to_display(date):
        """Converts a datetime.date object to ISO 8601 format"""
        try:
            dt = date.strftime("%-d %B %Y")
        except ValueError:
            dt = date
        return dt


def main():
    du = DateUtil()
    print(du.date_to_display("2018-10-08"))
    print(du.date_to_display("2018-10"))
    print(du.date_to_display("."))
    dt = datetime.date(2018, 10, 3)
    print(du.datetime_to_display(dt))


if __name__ == "__main__":
    main()
