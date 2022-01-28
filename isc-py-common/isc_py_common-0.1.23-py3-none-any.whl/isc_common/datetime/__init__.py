import datetime

def DateToDateTime(d):
    if isinstance(d, datetime.date):
        return datetime.datetime(d.year, d.month, d.day)
    else:
        return d


def DateToStr(date, mask='%d.%m.%Y', hours=3):
    if date is None:
        None
    if date is None:
        return None
    if isinstance(date, str):
        date = StrToDate(date)
    return datetime.datetime.strftime(date + datetime.timedelta(hours=hours), mask)


def DateTimeToStr(date, mask='%d.%m.%Y %H:%M:%S', hours=0):
    if date is None:
        return None
    if isinstance(date, str):
        date = StrToDate(date)
    return datetime.datetime.strftime(date + datetime.timedelta(hours=hours), mask)


def manth_name(month):
    if month == '01':
        return 'Январь'
    if month == '02':
        return 'Февраль'
    if month == '03':
        return 'Март'
    if month == '04':
        return 'Апрель'
    if month == '05':
        return 'Май'
    if month == '06':
        return 'Июнь'
    if month == '07':
        return 'Июль'
    if month == '08':
        return 'Август'
    if month == '09':
        return 'Сентябрь'
    if month == '10':
        return 'Октябрь'
    if month == '11':
        return 'Ноябрь'
    if month == '12':
        return 'Декабрь'


# Format Code List
# The table below shows all the format codes that you can use.
#
# Directive	Meaning	Example
# %a	Abbreviated weekday name.	Sun, Mon, ...
# %A	Full weekday name.	Sunday, Monday, ...
# %w	Weekday as a decimal number.	0, 1, ..., 6
# %d	Day of the month as a zero-padded decimal.	01, 02, ..., 31
# %-d	Day of the month as a decimal number.	1, 2, ..., 30
# %b	Abbreviated month name.	Jan, Feb, ..., Dec
# %B	Full month name.	January, February, ...
# %m	Month as a zero-padded decimal number.	01, 02, ..., 12
# %-m	Month as a decimal number.	1, 2, ..., 12
# %y	Year without century as a zero-padded decimal number.	00, 01, ..., 99
# %-y	Year without century as a decimal number.	0, 1, ..., 99
# %Y	Year with century as a decimal number.	2013, 2019 etc.
# %H	Hour (24-hour clock) as a zero-padded decimal number.	00, 01, ..., 23
# %-H	Hour (24-hour clock) as a decimal number.	0, 1, ..., 23
# %I	Hour (12-hour clock) as a zero-padded decimal number.	01, 02, ..., 12
# %-I	Hour (12-hour clock) as a decimal number.	1, 2, ... 12
# %p	Locale’s AM or PM.	AM, PM
# %M	Minute as a zero-padded decimal number.	00, 01, ..., 59
# %-M	Minute as a decimal number.	0, 1, ..., 59
# %S	Second as a zero-padded decimal number.	00, 01, ..., 59
# %-S	Second as a decimal number.	0, 1, ..., 59
# %f	Microsecond as a decimal number, zero-padded on the left.	000000 - 999999
# %z	UTC offset in the form +HHMM or -HHMM.
# %Z	Time zone name.
# %j	Day of the year as a zero-padded decimal number.	001, 002, ..., 366
# %-j	Day of the year as a decimal number.	1, 2, ..., 366
# %U	Week number of the year (Sunday as the first day of the week). All days in a new year preceding the first Sunday are considered to be in week 0.	00, 01, ..., 53
# %W	Week number of the year (Monday as the first day of the week). All days in a new year preceding the first Monday are considered to be in week 0.	00, 01, ..., 53
# %c	Locale’s appropriate date and time representation.	Mon Sep 30 07:06:05 2013
# %x	Locale’s appropriate date representation.	09/30/13
# %X	Locale’s appropriate time representation.	07:06:05
# %%	A literal '%' character.	%

def StrToDate(value_str, mask='%Y-%m-%dT%H:%M:%S', hours=0):
    if value_str is None:
        return None

    if isinstance(value_str, datetime.date):
        return value_str

    if len(value_str.split('.')) == 2:
        value_str = value_str.split('.')[0]
    res = datetime.datetime.strptime(value_str, mask)
    # return res
    return res + datetime.timedelta(hours=hours)
