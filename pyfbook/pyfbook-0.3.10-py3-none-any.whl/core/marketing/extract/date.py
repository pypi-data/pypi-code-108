import datetime
import json

DATE_FORMAT = "%Y-%m-%d"


def date_to_string(date):
    return date.strftime(DATE_FORMAT)


def string_to_date(string):
    return datetime.datetime.strptime(string, DATE_FORMAT)


def segment_month_date(start, end):
    """
    start : YYYY-MM-DD
    end : YYYY-MM-DD
    """
    start_datetime = string_to_date(start)
    end_datetime = string_to_date(end)
    result = []

    start_datetime = start_datetime.replace(day=1)
    end_datetime = end_of_month(end_datetime)

    while start_datetime != end_datetime + datetime.timedelta(days=1) and start_datetime <= datetime.datetime.today():
        inter = [date_to_string(start_datetime),
                 date_to_string(end_of_month(start_datetime))]
        result.append(inter)
        start_datetime = add_a_month(start_datetime)
    return result


def segment_year_date(start, end):
    """
    start : YYYY-MM-DD
    end : YYYY-MM-DD
    """
    start_datetime = string_to_date(start)
    end_datetime = string_to_date(end)
    result = []

    start_datetime = start_datetime.replace(day=1, month=1)
    end_datetime = end_datetime.replace(day=1, month=1, year=end_datetime.year + 1) + datetime.timedelta(days=-1)

    while start_datetime != end_datetime + datetime.timedelta(days=1) and start_datetime <= datetime.datetime.today():
        inter = [date_to_string(start_datetime),
                 date_to_string(start_datetime.replace(year=start_datetime.year + 1) + datetime.timedelta(days=-1))]
        result.append(inter)
        start_datetime = start_datetime.replace(year=start_datetime.year + 1)
    return result


def segment_quarter_date(start, end):
    """
    start : YYYY-MM-DD
    end : YYYY-MM-DD
    """
    start_datetime = string_to_date(start)
    end_datetime = string_to_date(end)
    result = []

    start_datetime = start_of_quarter(start_datetime)
    end_datetime = end_of_quarter(end_datetime)

    while start_datetime != end_datetime + datetime.timedelta(days=1) and start_datetime <= datetime.datetime.today():
        inter = [date_to_string(start_datetime),
                 date_to_string(end_of_quarter(start_datetime))]
        result.append(inter)
        start_datetime = add_a_quarter(start_datetime)
    return result


def segment_week_date(start, end):
    """
    start : YYYY-MM-DD
    end : YYYY-MM-DD
    """
    start_datetime = string_to_date(start)
    end_datetime = string_to_date(end)
    result = []

    start_datetime = start_datetime - datetime.timedelta(days=start_datetime.weekday())
    end_datetime = end_datetime - datetime.timedelta(days=end_datetime.weekday()) + datetime.timedelta(days=6)

    while start_datetime != end_datetime + datetime.timedelta(days=1) and start_datetime <= datetime.datetime.today():
        inter = [date_to_string(start_datetime),
                 date_to_string(start_datetime + datetime.timedelta(days=6))]
        result.append(inter)
        start_datetime = start_datetime + datetime.timedelta(days=7)
    return result


def add_a_month(date):
    try:
        nextmonthdate = date.replace(month=date.month + 1, day=1)
    except ValueError:
        if date.month == 12:
            nextmonthdate = date.replace(year=date.year + 1, month=1, day=1)
        else:
            # next month is too short to have "same date"
            # pick your own heuristic, or re-raise the exception:
            raise
    return nextmonthdate


def add_a_quarter(date):
    for i in range(3):
        date = add_a_month(date)
    return date


def remove_a_month(date):
    try:
        previousmonthdate = date.replace(month=date.month - 1, day=1)
    except ValueError:
        if date.month == 1:
            previousmonthdate = date.replace(year=date.year - 1, month=12, day=1)
        else:
            # next month is too short to have "same date"
            # pick your own heuristic, or re-raise the exception:
            raise
    return previousmonthdate


def end_of_month(date):
    return add_a_month(date) + datetime.timedelta(days=-1)


def end_of_quarter(date):
    while date.month not in [12, 3, 6, 9]:
        date = add_a_month(date)
    return end_of_month(date)


def start_of_quarter(date):
    while date.month not in [1, 4, 7, 10]:
        date = remove_a_month(date)
    return date.replace(day=1)


def define_date(year, month):
    since = datetime.date(year, month, 1).strftime(DATE_FORMAT)
    until = datetime.date.today().strftime(DATE_FORMAT)
    return since, until


def define_date_year(year):
    since = datetime.date(year, 1, 1)
    until = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    since = since.strftime(DATE_FORMAT)
    until = until.strftime(DATE_FORMAT)
    return since, until


def since_until_to_time_range(since, until):
    time_range = {
        "since": since,
        "until": until
    }
    time_range = json.dumps(time_range)
    return time_range


def since_until_to_time_ranges(since, until, time_increment):
    if time_increment == 'week':
        return [since_until_to_time_range(since, until) for since, until in segment_week_date(since, until)]
    if time_increment == 'month':
        return [since_until_to_time_range(since, until) for since, until in segment_month_date(since, until)]
    if time_increment == 'quarter':
        return [since_until_to_time_range(since, until) for since, until in segment_quarter_date(since, until)]
    if time_increment == 'year':
        return [since_until_to_time_range(since, until) for since, until in segment_year_date(since, until)]
    return 0


def set_last_year():
    last_year = datetime.date.today().year
    return define_date_year(last_year)


def set_default():
    return define_date(2018, 1)


def set_lifetime():
    return define_date(2017, 1)


def set_since_until(date_window):
    try:
        since = date_window["since"]
        until = date_window["until"]
    except TypeError or AttributeError:
        function_to_run = globals()["set_" + date_window]
        since, until = function_to_run()
    return since, until
