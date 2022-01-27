# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from datetime import datetime


def str2date(datestr, format='%d/%m/%y'):
    '''Convert a string to a date object'''
    dt = str2datetime(datestr, format=format)
    return datetime.date(dt)


def str2datetime(datestr, format='%d/%m/%y'):
    '''Convert a string to a datetime object'''
    return datetime.strptime(datestr, format)


def date2str(date, format='%Y-%m-%d'):
    '''Convert a datetime object to a string'''
    return date.strftime(format)


def date2date(datestr, fromfmt='%d/%m/%y', tofmt='%Y-%m-%d'):
    '''
    Convert a date in a string to another string, in a different
    format
    '''
    return date2str(str2date(datestr, fromfmt), tofmt)
