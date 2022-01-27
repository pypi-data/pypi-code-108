""" helpers file with general string / date functions """
import datetime


def strip_date(dt):
    # takes a datetime and only keeps the date
    if isinstance(dt, datetime.datetime):
        dt = datetime.datetime(dt.year, dt.month, dt.day).date()

    return dt


def to_datetime_date(date):
    return datetime.datetime.strptime(str(strip_date(date)), '%Y-%m-%d').date()


def to_string_date(date):
    return str(date)
