from datetime import datetime, timedelta

import pandas as pd


def date_handler(date_string, date_format="%Y-%m-%d"):
    """
    Takes a date string or phrase and returns the valid date in
    the specified format.
    :date_string: A phrase like "3_days_ago", "yesterday" or "today"
                     or a date string such as "2021-01-01".
    :date_format: The returned formatting of the date.
    """
    try:
        if date_string == "today":
            return datetime.now().strftime(date_format)
        if date_string == "yesterday":
            return (datetime.now() - timedelta(days=1)).strftime(date_format)
        if "_days_ago" in date_string:
            return phrase_to_date(phrase=date_string, date_format=date_format)
        return date_string
    except ValueError as err:
        raise ValueError(
            "StartDate requires a valid input "
            'such as "today", "yesterday" or "<int>_days_ago".'
        ) from err


def phrase_to_date(phrase, date_format="%Y-%m-%d"):
    """
    Takes a typical phrase such as "3_days_ago" and returns a
    date based on that phrase.
    :phrase: str. Something like 3_days_ago or 25_days_ago etc.
    :return: '%Y-%m-%d'
    """
    try:
        date_delta = int(phrase.split("_")[0])
        return (datetime.now() - timedelta(days=date_delta)).strftime(date_format)
    except ValueError as err:
        raise ValueError(
            f"Phrasing for date: {phrase} is not valid, "
            f"try something like: 3_days_ago"
        ) from err


def date_range(start_date, end_date, delta=timedelta(days=1)):
    """
    The range is inclusive, so both start_date and end_date will be returned.
    :start_date: The datetime object representing the first day in the range.
    :end_date: The datetime object representing the second day in the range.
    :delta: A datetime.timedelta instance, specifying the step interval. Defaults to one day.
    Yields:
        Each datetime object in the range.
    """

    start_date = date_handler(date_string=start_date)
    end_date = date_handler(date_string=end_date)

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    current_date = start_date
    while current_date <= end_date:
        yield current_date.strftime("%Y-%m-%d")
        current_date += delta


def filter_data_by_dates(
    start_date, end_date, date_field, data_frame: pd.DataFrame, date_fmt="%Y-%m-%d"
):
    """
    Takes a data frame and filters the data by given date field and
    date scopes that can be phrases.
    If no scope is added, imply current time is expected.
    """

    _now = datetime.now().strftime(date_fmt)
    if start_date is None:
        sd = _now
    else:
        sd = date_handler(start_date, date_fmt)

    if end_date is None:
        ed = _now
    else:
        ed = date_handler(end_date, date_fmt)

    print(f"Gathering data between {sd} and {ed}.")
    # filter data by given date field
    if sd is not None and ed is not None:
        data_frame["tmp_date"] = pd.to_datetime(data_frame[date_field])
        data_frame["tmp_date"] = data_frame["tmp_date"].dt.strftime(date_fmt)
        data_frame = data_frame[
            (
                data_frame["tmp_date"]
                >= datetime.strptime(sd, date_fmt).strftime(date_fmt)
            )
            & (
                data_frame["tmp_date"]
                <= datetime.strptime(ed, date_fmt).strftime(date_fmt)
            )
        ]
        data_frame = data_frame.drop("tmp_date", axis="columns")

    if len(data_frame.index) > 0:
        return data_frame

    print(f"No data for given date filter: {sd} to {ed}.")
    return None
