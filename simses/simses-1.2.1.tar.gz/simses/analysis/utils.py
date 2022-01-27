from calendar import isleap
from datetime import datetime

import pytz


def get_sum_for(data) -> float:
    return data[:].sum()


def get_mean_for(data) -> float:
    return data[:].mean()


def get_min_for(data) -> float:
    return data[:].min()


def get_max_for(data) -> float:
    return data[:].max()


def get_positive_values_from(data):
    _data = data[:].copy()
    _data[_data < 0] = 0
    return _data


def get_negative_values_from(data):
    _data = data[:].copy()
    _data[_data > 0] = 0
    return _data


def get_fractional_years(start_timestamp, end_timestamp):
    start_date = datetime.fromtimestamp(start_timestamp, tz=pytz.UTC)
    end_date = datetime.fromtimestamp(end_timestamp, tz=pytz.UTC)
    diffyears = end_date.year - start_date.year
    difference = end_date - start_date.replace(end_date.year)
    days_in_year = isleap(end_date.year) and 366 or 365
    total_fractional_years = diffyears + (difference.days + difference.seconds / 86400.0) / days_in_year
    return total_fractional_years
