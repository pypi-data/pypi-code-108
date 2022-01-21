"""Time management helper.

stephane.ploix@g-scop.grenoble-inp.fr
"""

import datetime
import time

def epochtimems_to_stringdate(epochtimems, date_format='%d/%m/%Y %H:%M:%S'):
    """Transform an epoch time  into a string representation.

    :param epochtimems: epoch time in milliseconds
    :type epochtimems: int
    :return: string representation '%d/%m/%Y %H:%M:%S'
    :rtype: datetime.datetime
    """
    return time.strftime(date_format, time.localtime(epochtimems // 1000))


def epochtimems_to_datetime(epochtimems):
    """Transform an epoch time into an internal datetime representation.

    :param epochtimems: epoch time in milliseconds
    :type epochtimems: int
    :return: internal datetime representation
    :rtype: datetime.datetime
    """
    return datetime.datetime.fromtimestamp(epochtimems // 1000)


def datetime_to_epochtimems(a_datetime):
    """Transform a an internal datetime representation into a epoch time.

    :param a_datetime: internal datetime representation
    :type a_datetime: datetime to be converted
    :return: epoch time in milliseconds
    :rtype: int
    """
    return a_datetime.timestamp() * 1000


def stringdate_to_epochtimems(stringdatetime, date_format='%d/%m/%Y %H:%M:%S'):
    """Transform a date string representation into an epoch time.

    :param stringdatetime: date string representation '%d/%m/%Y %H:%M:%S'
    :type stringdatetime: str
    :return: epoch time in milliseconds
    :rtype: int
    """
    stringdatetime_secs_ms = stringdatetime.split(',')
    epochdatems = int(time.mktime(time.strptime(stringdatetime_secs_ms[0], date_format)) * 1000)
    if len(stringdatetime_secs_ms) > 1:
        epochdatems = epochdatems + int(stringdatetime_secs_ms[1])
    return epochdatems


def datetime_to_stringdate(a_datetime, date_format='%d/%m/%Y %H:%M:%S'):
    """Transform a datetime representation into a datetime internal format.

    :param a_datetime: internal datetime representation
    :type a_datetime: datetime.datetime
    :return: stringdatetime: date string representation '%d/%m/%Y %H:%M:%S'
    :rtype: str
    """
    return a_datetime.strftime(date_format)


def stringdate_to_datetime(stringdatetime, date_format='%d/%m/%Y %H:%M:%S'):
    """Transform a date string representation into an internal datetime representation.

    :param stringdatetime: date string representation '%d/%m/%Y %H:%M:%S'
    :type stringdatetime: str
    :return: internal datetime representation
    :rtype: datetime.datetime
    """
    return datetime.datetime.fromtimestamp(time.mktime(time.strptime(stringdatetime, date_format)))


def epochtimems_to_timequantum(epochtimems, timequantum_duration_in_secondes):
    """Transform an epoch time into a rounded discrete epoch time according to a given time quantum (sampling period).

    :param epochtimems: epoch time in milliseconds
    :type epochtimems: int
    :param timequantum_duration_in_secondes: time quantum duration (sampling period) in seconds
    :type timequantum_duration_in_secondes: int
    :return: rounded discrete epoch time in milliseconds
    """
    return (epochtimems // (timequantum_duration_in_secondes * 1000)) * timequantum_duration_in_secondes * 1000


def get_stringdate_with_day_delta(numberofdays=0, date_format='%d/%m/%Y %H:%M:%S'):
    """Compute a date from today minus a given day delta.

    :param numberofdays: number of day to remove to the current date, defaults to 0
    :type numberofdays: int, optional
    :param date_format: date format, defaults to '%d/%m/%Y %H:%M:%S'
    :type date_format: str, optional
    :return: the date in the past
    :rtype: datetime.datetime
    """
    return (datetime.datetime.now() - datetime.timedelta(days=numberofdays)).strftime(date_format)


def current_stringdate(date_format='%d/%m/%Y %H:%M:%S'):
    """Return the current date in string format.

    :param date_format: the string format, defaults to '%d/%m/%Y %H:%M:%S'
    :type date_format: str, optional
    :return: current date in string
    :rtype: str
    """
    return time.strftime(date_format, time.localtime())


def current_epochtimems():
    """Return current date in epoch time format.

    :return: epoch time number of miliseconds
    :rtype: int
    """
    return int(time.mktime(time.localtime()) * 1000)
