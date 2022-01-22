
"""Age (date subtraction) routines.
"""

from datetime import date as _date
from calendar import monthrange as _monthrange, isleap as _isleap


class age(object):
    "The number of years, months, and days since date of birth."
    def __init__(self, dob, today=None):
        today = today or _date.today()
        if dob is None:
            self.years = 0
            self.months = 0
            self.days = 0
            return

        y = today.year - dob.year
        m = today.month - dob.month
        d = today.day - dob.day

        while m < 0 or d < 0:
            while m < 0:
                y -= 1
                m = 12 + m  # m is negative
            if d < 0:
                m -= 1
                days = _days_previous_month(today.year, today.month)
                d = max(0, days - dob.day) + today.day

        self.years = y
        self.months = m
        self.days = d

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return (self.years == other.years
                and self.months == other.months
                and self.days == other.days)

    def __repr__(self):
        return '(%d, %d, %d)' % (self.years, self.months, self.days)


def next_birthday(birthday, today=None):
    "Return the date of the next birthday for someone born on date `birthday`."
    if today is None:
        today = _date.today()

    y, m, d = birthday.year, birthday.month, birthday.day

    y = today.year  # find the birthday this year.

    if (today.month, today.day) > (m, d):
        # if the birthday has passed, the next one is next year
        y += 1

    if not _isleap(y) and (m, d) == (2, 29):
        # Birthdays on the 29th of February are celebrated
        # on the 28th in non-leap years.
        d = 28

    return _date(y, m, d)


def birthday_this_year(birthday, today=None):
    "Return the date of the birthday in the current year."
    if today is None:
        today = _date.today()
    return next_birthday(birthday, _date(today.year, 1, 1))


def previous_birthday(birthday, today=None):
    """Return the previous birthday relative to ``today``.
    """
    if today is None:
        today = _date.today()
    return next_birthday(birthday, years_ago(1, today))


def years_ago(n, today=None):
    "The date that is `n` years before `today`."
    today = today or _date.today()
    pastyear = today.year - n
    _, pdays = _monthrange(pastyear, today.month)
    day_ok = today.day <= pdays
    if day_ok:
        pastday = today.day
        pastmonth = today.month
    else:
        pastday = _days_previous_month(pastyear, today.month)
        pastmonth = _past_month(today.month)
    res = _date(pastyear, pastmonth, pastday)
    return res


def days_ago(n, dato=None):
    "The date that is `n` days before `dato` (or today)."
    today = dato or _date.today()
    return _date.fromordinal(today.toordinal() - n)


def weeks_ago(n, today=None):
    "The date that is `n` weeks before `today`."
    today = today or _date.today()
    if n != 0:
        ret = _date.fromordinal(today.toordinal() - (7 * n))
    else:
        ret = _date.today()
    return ret


def _past_month(m):
    "Subtract 1 from month."
    if m == 1:
        return 12
    else:
        return m - 1


def _days_previous_month(y, m):
    "The number of days in the month before year `y` and month `m`."
    m -= 1
    if m == 0:
        y -= 1
        m = 12
    _, days = _monthrange(y, m)
    return days
