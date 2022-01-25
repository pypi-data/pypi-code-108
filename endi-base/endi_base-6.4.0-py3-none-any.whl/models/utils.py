"""
    Usefull functions
"""
import time
import datetime

from sqlalchemy import (
    func,
    cast,
)
from sqlalchemy.types import NullType
from sqlalchemy import BigInteger

DEFAULT_DATE = datetime.date(2000, 1, 1)


def format_to_taskdate(value):
    """
        format a datetime.date object to a 'taskdate' format:
        an integer composed from a string YYYYmmdd
        Sorry .... it's not my responsability
    """
    if value is None:
        return None
    elif isinstance(value, datetime.date):
        if value.year < 1900:
            value.year = 1901
        return int(value.strftime("%Y%m%d"))
    else:
        return int(value)


def get_current_timestamp():
    """
        returns current time
    """
    return int(time.time())


def non_null_sum(column, *args, **kwargs):
    """
    Cast the sqlalchemy built with func.sum to the same type as the column
    being summed

    Usefull to avoid getting decimal when we expect an int
    :param obj column: The SqlAlchemy column (e.g : Payment.amount)
    :returns: A SqlAlchemy query option (passed to Dbsession.query)
    """
    query = func.sum(column, *args, **kwargs)
    # Prevent Decimal typing when agregating
    query = func.ifnull(query, 0)
    if not isinstance(column.type, NullType):
        query = cast(query, column.type.__class__)
    else:
        query = cast(query, BigInteger)
    return query
