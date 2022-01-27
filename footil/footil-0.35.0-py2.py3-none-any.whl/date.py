"""Helpers for date manipulation."""
import datetime
from dateutil.relativedelta import relativedelta
from typing import Optional

DATE_FMT = '%Y-%m-%d'


def _modify_date(
    dt: datetime.date,
    modify_fun: callable,
    args: Optional[tuple] = None,
        kwargs: Optional[dict] = None) -> datetime.date:
    if not args:
        args = []
    if not kwargs:
        kwargs = {}
    return modify_fun(dt, *args, **kwargs)


def to_date(
    dt: str,
        fmt: Optional[str] = DATE_FMT) -> datetime.date:
    """Convert date string of custom format to datetime.date object."""
    return datetime.datetime.strptime(dt, fmt).date()


def to_string(
    dt: datetime.date,
        fmt: Optional[str] = DATE_FMT) -> str:
    """Convert datetime.date object to custom format date string."""
    return dt.strftime(fmt)


def get_first_day_date(
    dt: datetime.date,
        months: int = 0) -> datetime.date:
    """Return date by replacing day to be first day of the month.

    Args:
        dt (datetime.date): datetime.date object to modify.
        months (int): x month
            (0 - this month, 1 - next month, -1 - last month, ...)

    Returns:
        datetime.date: modified date as datetime.date object with day
            being first of the month.

    """
    return _modify_date(
        dt,
        lambda dt: dt + relativedelta(day=1, months=months))


def get_last_day_date(
    dt: datetime.date,
        months: int = 0) -> datetime.date:
    """Return date by replacing day to be last day of the month.

    Args:
        dt (datetime.date): datetime.date object to modify.
        months (int): x month
            (0 - this month, 1 - next month, -1 - last month, ...)

    Returns:
        datetime.date: modified date as datetime.date object with day
            being last of the month.

    """
    return _modify_date(
        dt,
        lambda dt: dt + relativedelta(day=1, days=-1, months=(months + 1)))


def get_first_day_date_str(
    dt: str,
    fmt: Optional[str] = DATE_FMT,
    new_fmt: Optional[str] = False,
        months: int = 0) -> str:
    """Return date by replacing day to be first day of the month.

    Args:
        dt (str): date as string to modify.
        fmt (str): format to convert from (default: {DATE_FMT})
        new_fmt (str): format to convert to. If not set, will use
            fmt variable format. (default: {False})
        months (int): x month
            (0 - this month, 1 - next month, -1 - last month, ...)

    Returns:
        str: modified date with day being first of the month.

    """
    if not new_fmt:
        new_fmt = fmt
    date_fmt = to_date(dt, fmt=fmt)
    modified_dt = get_first_day_date(date_fmt, months=months)
    return to_string(modified_dt, fmt=new_fmt)


def get_last_day_date_str(
    dt: datetime.date,
    fmt: Optional[str] = DATE_FMT,
    new_fmt: Optional[str] = False,
        months: int = 0) -> str:
    """Return date by replacing day to be last day of the month.

    Args:
        dt (str): date as string to modify.
        fmt (str): format to convert from (default: {DATE_FMT})
        new_fmt (str): format to convert to. If not set, will use
            fmt variable format. (default: {False})
        months (int): x month
            (0 - this month, 1 - next month, -1 - last month, ...)

    Returns:
        str: modified date with day being last of the month.

    """
    if not new_fmt:
        new_fmt = fmt
    date_fmt = to_date(dt, fmt=fmt)
    modified_dt = get_last_day_date(date_fmt, months=months)
    return to_string(modified_dt, fmt=new_fmt)
