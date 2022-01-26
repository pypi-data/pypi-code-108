"""
Datetime utilities.

TODO: consider splitting this off into its own independent python package.

WARNING: Converting datetime string to datetime object (or timestamp) could 
        silently give incorrect values if the timezone in the string is not UTC.
        The issue arises from parsing the string, and interpreting the timezone.
        In particular, the dateutil.tz.gettz(tzname) function.
        eg:
            '2021-12-19 13:39:27 AEDT'  (Australian Easter Daylight Time) 
                                        Might assign a `tzlocal()` timezone
            '2021-12-18 18:39:27 PST'   (Pacific Standard Time) 
                                        returns a timezone-unaware datetime.
"""
import datetime
import dateutil

DESIRED_TIMEZONE = "UTC"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"

def set_timezone(
    dt:datetime.datetime,
    tz:str = "UTC",
):
    """Given a datetime object, it sets the timezone to the given timezone.
    
    Args:
        dt (datetime object): The datetime object to set the timezone on.
        timezone (str, optional): The timezone to set the datetime object to. Eg
            "UTC", or "Australia/Melbourne". Defaults to "UTC".
    """
    tzinfo = dateutil.tz.gettz(tz)
    dt = dt.replace(tzinfo=tzinfo)
    return dt


def timestamp_to_datetime(
    timestamp:float,
    tz:str = "UTC",
    unit:str = "ms",
) -> datetime.datetime:
    """Convert a unix timestamp to a datetime object. By default, it sets it to
    UTC timezone aware datetime.

    Args:
        timestamp (float): The unix timestamp to convert, as a float, or 
            something that can be typecast to a float.
        timezone (str, optional): The timezone to use, eg "UTC", or 
            "Australia/Melbourne". Defaults to "UTC".
        unit (str, optional): The unit of the timestamp. Can be "ms" or "s".
    """
    unit = unit.lower()
    timestamp = float(timestamp)

    # Convert timestamp to seconds (as required by python datetime library)
    if unit == "ms":
        timestamp = timestamp / 1000.
    elif unit == "s":
        pass
    else:
        legal_units = {"ms", "s"}
        raise ValueError(f"`unit` must be one of {legal_units}, received {unit}.")

    if tz is None:
        dt = datetime.datetime.fromtimestamp(timestamp)
    else:
        tzinfo = dateutil.tz.gettz(tz)
        dt = datetime.datetime.fromtimestamp(timestamp, tz=tzinfo)
    return dt

def timestamp_to_datetime_str(
    timestamp:float,
    tz:str = "UTC",
    unit: str = "ms",
    format:str = DATETIME_FORMAT
) -> str:
    """Convert a unix timestamp to a datetime string. By default, it sets it to
    UTC timezone aware datetime.

    Args:
        timestamp (float): The unix timestamp to convert, as a float, or 
            something that can be typecast to a float.
        timezone (str, optional): The timezone to use, eg "UTC", or 
            "Australia/Melbourne". Defaults to "UTC".
        unit (str, optional): The unit of the timestamp. Can be "ms" or "s".
        format (str, optional): The format to use for the datetime string.
    """
    dt = timestamp_to_datetime(timestamp, tz=tz, unit=unit)
    return dt.strftime(format)


def parse_datetime_str(datetime_str:str, tz:str=None)->datetime.datetime:
    """Given a string in the format of '2021-12-05 12:50:00', or 
    '2021-12-05 12:50:00 UTC' it converts it to a datetime object.

    Note: 
        It is better to explicitly set the timezone using the `tz` argument,
        rather than letting it interpret the timezone from the datetime string.
        This is because dateutil.parser.parse() is not able to parse timezones
        such as "AEDT" or "PST" very well.

    Args:
        datetime_str (str): The datetime string to parse.
        tz (str, optional): Set the timezone. Note, that if the string already
            had a timezone specified, then this overrides it. 
            eg "UTC", or "Australia/Melbourne". 
            Defaults to `None`, which means it tries to extract timezone from 
            the string. Otherwise, it sets it to timezone-unaware datetime.
    """
    # SEPARATE THE TIMZEONE FROM THE DATETIME STRING
    embedded_tz = None
    pattern = r"(.*[\d])([\D]*$)"
    match = re.search(pattern, datetime_str)
    if match is not None:
        groups = match.groups()
        datetime_str = groups[0].strip()
        embedded_tz = groups[1].strip()
        if embedded_tz == "":
            embedded_tz = None
        if embedded_tz == "Z":
            embedded_tz = "UTC"
    
    # DECIDE WHICH TZ TO USE
    tz = tz if tz is not None else embedded_tz
    tzinfo = None if tz is None else dateutil.tz.gettz(tz)
    if tzinfo is None: 
        if tz is None:
            print(f"WARNING: No timezone specified. Setting to timezone-unaware.")
        else:
           print(f"WARNING: Could not parse timezone '{tz}'. Setting to timezone-unaware.")

    # PARSE THE DATETIME STRING - and assign timezone
    dt = dateutil.parser.parse(datetime_str)
    dt = dt.replace(tzinfo=tzinfo)
    return dt


def datetime_str_to_timestamp(datetime_str, tz=None, unit="ms"):
    """Given a string in the format of '2021-12-05 12:50:00', or 
    '2021-12-05 12:50:00 UTC' it converts it to a unix timestamp.

    Note: 
        It is better to explicitly set the timezone using the `tz` argument,
        rather than letting it interpret the timezone from the datetime string.
        This is because dateutil.parser.parse() is not able to parse timezones
        such as "AEDT" or "PST" very well.

    Args:
        datetime_str (str): The datetime string to parse.
        tz (str, optional): Set the timezone. Note, that if the string already
            had a timezone specified, then this overrides it. 
            eg "UTC", or "Australia/Melbourne". 
            Defaults to `None`, which means it tries to extract timezone from 
            the string. Otherwise, it sets it to timezone-unaware datetime.
    """
    dt = parse_datetime_str(datetime_str, tz=tz)
    print(dt)

    # CONVERT TO TIMESTAMP
    unit = unit.lower().strip()
    if unit == "ms":
        multiplier = 1000
    elif unit == "s":
        multiplier = 1
    else:
        raise ValueError(f"`unit` must be one of ['ms', 's'], received {unit}.")
    ts = int(dt.timestamp() * multiplier)
    return ts


def convert_timearg_as_datetime(t):
    tz = dateutil.tz.gettz(DESIRED_TIMEZONE)
    if isinstance(t, datetime.datetime):
        dt = t
        if dt.tzinfo is not None:
            dt = t.replace(tzinfo=tz)
        else:
            dt = dt.astimezone(tz)
    elif isinstance(t, str):
        dt = dateutil.parser.parse(t)
        dt = dt.replace(tzinfo=tz)
    else:
        ts = float(t)
        dt = datetime.datetime.fromtimestamp(ts, tz=tz)
    return dt

def convert_timearg_as_timestamp(t, unit="ms", tz="UTC"):
    """A flexible way to receive timestamp argument in many different formats.
    Either as an actual timestamp, a datetime, or a datetime string. Parses any
    one of those formats into a timestamp value.
    """
    if isinstance(t, datetime.datetime):
        if unit == "ms":
            multiplier = 1000
        elif unit == "s":
            multiplier = 1
        else:
            raise ValueError(f"`unit` must be one of ['ms', 's'], received {unit}.")
        ts = int(t.timestamp() * multiplier)
    elif isinstance(t, str):
        ts = datetime_str_to_timestamp(t, tz=tz, unit=unit)
    else:
        ts = int(float(t))
    return ts


# ##############################################################################
#                      Mapping short tzname to timezone regions
#                      eg: AEDT -> "Australia/Melbourne"
#                      for parsing datetime strings using dateutil.parser
# ##############################################################################
# import os
# import dateutil.tz as dtz
# import pytz
# import datetime as dt
# import collections

# result=collections.defaultdict(list)
# for name in pytz.common_timezones:
#     timezone=dtz.gettz(name)
#     now=dt.datetime.now(timezone)
#     offset=now.strftime('%z')
#     abbrev=now.strftime('%Z')
#     result[offset].append(name)
#     result[abbrev].append(name)
# print(result)
# result.keys()

# result["AEST"]
# result["AEDT"]


# # LIST ALL TIMEZONES NAMES
# import pytz
# pytz.all_timezones
