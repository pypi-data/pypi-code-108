#!/usr/bin/env python3
"""
Module LOCALIZE -- PLIB3 Localization Utilities
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains useful localization functions that
should be in the standard library but aren't. :p

Sanity checks since the functions taking ``datetime``
arguments use a different API:

    >>> from datetime import datetime
    >>> dt = datetime.now()
    >>> assert weekdayname(dt.weekday(), dt=True) == dt_weekdayname(dt)
    >>> assert weekdayname_long(dt.weekday(), dt=True) == dt_weekdayname_long(dt)
    >>> assert monthname(dt.month) == dt_monthname(dt)
    >>> assert monthname_long(dt.month) == dt_monthname_long(dt)
"""

import locale

try:
    from locale import nl_langinfo
    
    
    # We factor this out for easier handling of platforms
    # that don't have nl_langinfo, below
    
    def get_langinfo(infotype, key):
        try:
            return nl_langinfo(
                getattr(locale, '{}_{}'.format(infotype, key))
            )
        except AttributeError:
            raise RuntimeError("Invalid locale langinfo code: {}_{}".format(infotype, key))


except ImportError:
    # Some platforms don't have the nl_langinfo function,
    # so we have to improvise; all we can do is use
    # English names since we have no other info to go by,
    # but we do include an extra parameter that can be
    # used to provide a different dictionary for lookups
    # directly to this function, bypassing the normal API
    
    LOCALE_MAP = {
        'ABDAY': {
            1: "Sun",
            2: "Mon",
            3: "Tue",
            4: "Wed",
            5: "Thu",
            6: "Fri",
            7: "Sat",
        },
        'DAY': {
            1: "Sunday",
            2: "Monday",
            3: "Tuesday",
            4: "Wednesday",
            5: "Thursday",
            6: "Friday",
            7: "Saturday",
        },
        'ABMON': {
            1: "Jan",
            2: "Feb",
            3: "Mar",
            4: "Apr",
            5: "May",
            6: "Jun",
            7: "Jul",
            8: "Aug",
            9: "Sep",
            10: "Oct",
            11: "Nov",
            12: "Dec",
        },
        'MON': {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        },
    }
    
    
    def get_langinfo(infotype, key, locale_map=LOCALE_MAP):
        try:
            return locale_map[infotype][key]
        except KeyError:
            raise RuntimeError("Invalid locale langinfo code: {}_{}".format(infotype, key))


weekdays = iso_weekdays = set([1, 2, 3, 4, 5, 6, 7])
dt_weekdays = set([0, 1, 2, 3, 4, 5, 6])


def _convert_weekday(weekday, dt, iso):
    if iso:
        if weekday not in iso_weekdays:
            raise ValueError("{} is not a valid ISO weekday number".format(weekday))
    elif dt:
        if weekday not in dt_weekdays:
            raise ValueError("{} is not a valid datetime weekday number".format(weekday))
    else:
        if weekday not in weekdays:
            raise ValueError("{} is not a valid weekday number".format(weekday))
    return (
        weekday % 7 + 1 if iso else
        (weekday + 1) % 7 + 1 if dt else
        weekday
    )


def weekdayname(weekday, dt=False, iso=False):
    """Return abbreviated weekday name for weekday.
    
    This function assumes that ``weekday`` follows the
    ``locale`` module's convention (where Sunday = 1),
    unless one of the keywords is true. If ``dt`` is
    true and ``iso`` is false, the convention used by
    the ``weekday`` method of a ``date`` or ``datetime``
    object is used (so Monday = 0 and Sunday = 6); if
    ``iso`` is true, the ISO convention is assumed
    (Monday = 1 and Sunday = 7). Why there have to be
    three different conventions for this is beyond me.
    """
    weekday = _convert_weekday(weekday, dt, iso)
    return get_langinfo('ABDAY', weekday)


def dt_weekdayname(dt):
    """Return abbreviated weekday name for datetime.
    """
    return dt.strftime("%a")


def weekdayname_long(weekday, dt=False, iso=False):
    """Return long weekday name for weekday.
    
    The parameters are treated the same as for the
    ``weekdayname`` function.
    """
    weekday = _convert_weekday(weekday, dt, iso)
    return get_langinfo('DAY', weekday)


def dt_weekdayname_long(dt):
    """Return long weekday name for datetime.
    """
    return dt.strftime("%A")


def monthname(month):
    """Return abbreviated month name for month.
    """
    return get_langinfo('ABMON', month)


def dt_monthname(dt):
    """Return abbreviated month name for datetime.
    """
    return dt.strftime("%b")


def monthname_long(month):
    """Return long month name for month.
    """
    return get_langinfo('MON', month)


def dt_monthname_long(dt):
    """Return long month name for datetime.
    """
    return dt.strftime("%B")


if __name__ == '__main__':
    import doctest
    doctest.testmod()
