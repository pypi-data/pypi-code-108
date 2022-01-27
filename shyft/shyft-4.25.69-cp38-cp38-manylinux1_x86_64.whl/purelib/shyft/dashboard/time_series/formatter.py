from typing import List, Optional, Iterable

import numpy as np
import calendar
from shyft.time_series import Calendar


def conditional_time_formatter(time_input: Iterable, time_zone: Optional[str] = None) -> List[str]:
    """
    Create human readable formatting of UTC time conditional on dt.

    Assumption of an equidistant dt, time in UTC
    Formatting and converting time values for the table view

    Additional time_zone can be provided to convert from UTC to time_zone

    Examples
    --------

    dt == DAY:
    ['2018.03.12 (W.11)', '2018.03.13 (W.11)', '2018.03.14 (W.11)']

    dt == WEEK:
    ['2018 Week 11', '2018 Week 12', '2018 Week 13']

    dt == MONTH:
    ['2018 Mar', '2018 Apr', '2018 May']

    dt == QUARTER:
    ['2018 Q.1', '2018 Q.2', '2018 Q.3']

    dt == YEAR:
    ['2018', '2019', '2020']

    else:
    ['2018.03.12 16:26', '2018.03.12 17:26', '2018.03.12 18:26']

    Parameters
    ----------
    time_input: numpy array with utc time
    time_zone: Optional time_zone to convert time to

    Returns
    -------
    time_formatted: list with reformatted times
    """

    cal = Calendar(time_zone or 0)
    time_tuples = [(cal.calendar_week_units(int(t)), cal.calendar_units(int(t))) for t in time_input]
    dts = [[d for d in [cal.DAY, cal.WEEK, cal.MONTH, cal.QUARTER, cal.YEAR]
            if cal.diff_units(int(time_input[i]), int(time_input[i + 1]), d) == 1] for i in
           range(0, len(time_input) - 1, 2)]
    dt = [min(d) for d in dts if d]
    time_formatted =[]
    if not dt:
        time_formatted = [f'{greg.year}.{greg.month:>{0}2}.{greg.day:>{0}2} {greg.hour:>{0}2}:{greg.minute:>{0}2}'
                          for iso, greg in time_tuples]
        return time_formatted
    dt = min(np.unique(dt))
    if dt == cal.DAY:
        time_formatted = [f'{greg.year}.{greg.month:>{0}2}.{greg.day:>{0}2} (W.{iso.iso_week})' for iso, greg in
                          time_tuples]
    elif dt == cal.WEEK:
        time_formatted = [f"{iso.iso_year} Week {iso.iso_week:>{0}2}" for iso, greg in time_tuples]
    elif dt == cal.MONTH:
        time_formatted = [f"{greg.year} {calendar.month_abbr[greg.month]}" for iso, greg in time_tuples]
    elif dt == cal.QUARTER:
        time_formatted = [f"{cal.calendar_units(t).year} Q.{cal.quarter(t)}" for t in time_input]
    elif dt == cal.YEAR:
        time_formatted = [f'{greg.year}' for iso, greg in time_tuples]
    return time_formatted


def basic_time_formatter(time_input: Iterable, time_zone: Optional[str] = None) -> List[str]:
    """
    Create human readable formatting of UTC time

    Additional time_zone can be provided to convert from UTC to time_zone

    Examples
    --------
    ['2018.03.12 16:26', '2018.03.12 17:26', '2018.03.12 18:26']

    Parameters
    ----------
    time_input: numpy array with utc time
    time_zone: Optional time_zone to convert time to

    Returns
    -------
    time_formatted: list with reformatted times
    """
    cal = Calendar(time_zone or 0)
    greg_time = [cal.calendar_units(int(t)) for t in time_input]
    time_formatted = [f'{greg.year}.{greg.month:>{0}2}.{greg.day:>{0}2} {greg.hour:>{0}2}:{greg.minute:>{0}2}'
                      for greg in greg_time]
    return time_formatted
