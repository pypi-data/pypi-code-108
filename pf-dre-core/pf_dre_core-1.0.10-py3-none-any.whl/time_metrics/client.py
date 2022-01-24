# Built-in Modules
import re
import os
import logging
from datetime import timedelta, datetime
from typing import Union, Optional, List

# Third Party Modules
from astral import Observer
from astral import sun
import pandas as pd
import numpy as np
from pytz import timezone

logger = logging.getLogger(__name__)


def get_sun_elevation(ts):
    """
    :param ts:
    :return: The sun elevation for a given timestamp
    """
    # Default to the location of the St Lucia Campus
    # TODO: These coords should be pulled from the DB
    #  (integrate into dre-database-api)
    long = 153.014008
    lat = -27.497999
    observer = Observer(lat, long)
    return sun.elevation(observer, pd.to_datetime(ts))


def is_public_holiday(dt, hols):
    """
    :param dt Localized datetime numpy datetime64
    :param hols List of dates of public holidays
    :return: 1 if the date exists in the list of holidays
    """
    if dt.tz_convert(tz='Australia/Brisbane').strftime("%d-%m-%Y") in hols:
        return 1
    else:
        return 0


def is_working_hours(dt):
    """
    :param dt Localized datetime numpy datetime64
    :return: 1 or 0 depending on working hours threshold
    """
    if 7 <= dt.tz_convert(tz='Australia/Brisbane').hour < 18:
        return 1
    else:
        return 0


def get_dow(dt):
    """
    :param dt Localized datetime numpy datetime64
    :return: Day of the week
    """
    return dt.tz_convert(tz='Australia/Brisbane').dayofweek


def is_weekend(dt):
    if 5 <= dt.tz_convert(tz='Australia/Brisbane').dayofweek <= 6:
        return 1
    else:
        return 0


def get_time_related_timeseries(idx: pd.DatetimeIndex,
                                features: List[str],
                                hols: List[str]) -> \
        Union[pd.DataFrame, None]:
    """
    :param idx: Datetime index which defines the duration and resolution of
    the resulting DataFrame.
    :param features: A list of features to be included in the resulting
    DataFrame
    :param hols: A list of dates as strings representing Brisbane Timezone
    public holidays. TODO handle other timezones
    :return: time dependent DataFrame with datetime index idx.
    """
    features_df = None
    if features is None or type(features) != list:
        return features_df
    features_df = pd.DataFrame(index=idx)
    # Initialize Supported time series
    day = 24*60*60
    year = 365.2425*day
    if "sunElevation" in features:
        features_df['sunElevation'] = idx.to_series().apply(get_sun_elevation)
    if "daylight" in features:
        features_df['daylight'] = idx.to_series().apply(
            lambda x: 1 if get_sun_elevation(x) > 0 else 0)
    if "publicHoliday" in features:
        features_df['publicHoliday'] = idx.to_series().apply(
            is_public_holiday, args=(hols,))
    if "weekend" in features:
        features_df['weekend'] = idx.to_series().apply(is_weekend)
    if "workingHours" in features:
        features_df['workingHours'] = idx.to_series().apply(is_working_hours)
    if "dow" in features:
        features_df['dow'] = idx.to_series().apply(get_dow)
    if "day" in features:
        timestamp_s = idx.to_series().map(datetime.timestamp)
        features_df['daySin'] = np.sin(timestamp_s * (2 * np.pi / day))
        features_df['dayCos'] = np.cos(timestamp_s * (2 * np.pi / day))
    if "year" in features:
        timestamp_s = idx.map(datetime.timestamp)
        features_df['yearSin'] = np.sin(timestamp_s * (2 * np.pi / year))
        features_df['yearCos'] = np.cos(timestamp_s * (2 * np.pi / year))
    return features_df
