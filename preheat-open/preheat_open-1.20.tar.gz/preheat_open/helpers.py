from datetime import date, datetime, timedelta, timezone
from typing import Union

import dateutil.parser
from dateutil.tz import tzutc

from preheat_open import TIMEZONE

utc = timezone.utc


def timestep_start(step, t):

    if step in ["second", "1s"]:
        t_start = t.replace(microsecond=0)
    elif step == "15s":
        sec_start = int(t.second / 15) * 15
        t_start = t.replace(microsecond=0, second=sec_start)
    elif step == "30s":
        sec_start = int(t.second / 30) * 30
        t_start = t.replace(microsecond=0, second=sec_start)
    elif step in ["minute", "1min"]:
        t_start = t.replace(microsecond=0, second=0)
    elif step == "5min":
        min_start = int(t.minute / 5) * 5
        t_start = t.replace(microsecond=0, second=0, minute=min_start)
    elif step == "15min":
        min_start = int(t.minute / 15) * 15
        t_start = t.replace(microsecond=0, second=0, minute=min_start)
    elif step == "30min":
        min_start = int(t.minute / 30) * 30
        t_start = t.replace(microsecond=0, second=0, minute=min_start)
    elif step == "hour":
        t_start = t.replace(microsecond=0, second=0, minute=0)
    elif step == "day":
        t_start = t.replace(microsecond=0, second=0, minute=0, hour=0)
    elif step == "month":
        t_start = t.replace(microsecond=0, second=0, minute=0, hour=0, day=1)
    elif step == "year":
        t_start = t.replace(microsecond=0, second=0, minute=0, hour=0, day=1, month=1)
    else:
        raise Exception("Unknown step: " + step)

    return t_start


def now(step=None, tz=TIMEZONE):
    t = datetime.now(tz=tz)
    if step is None:
        return t
    else:
        return timestep_start(step, t)


def __enforce_imports():
    date.today() + timedelta(days=2)


def datetime_convert(param):
    if isinstance(param, datetime):
        dt = param
    elif isinstance(param, str):
        dt = dateutil.parser.parse(param)
    else:
        raise TypeError(f"No conversion from type: {type(param)}")

    return dt if dt.tzinfo is not None else dt.astimezone(TIMEZONE)


def sanitise_datetime_input(t: Union[datetime, str]) -> datetime:

    if isinstance(t, str):
        out = datetime_convert(t)
    else:
        out = t
    return out.astimezone(tzutc())


def time_resolution_aliases(time_resolution):
    if time_resolution in ["minute", "5min"]:
        return "5T"
    elif time_resolution == "hour":
        return "H"
    elif time_resolution == "day":
        return "D"
    elif time_resolution == "week":
        return "W"
    elif time_resolution == "month":
        return "MS"
    elif time_resolution == "year":
        return "YS"
    else:
        return None


def convenience_result_list_shortener(result):
    n_results = len(result)
    if n_results > 1:
        return result
    elif n_results == 0:
        return None
    else:
        return result[0]


def list_to_string(list2use, separator=",") -> str:
    """
    Helper function to turn list into string, e.g. comma separated (default).
    """

    if isinstance(list2use, list):
        res = separator.join(map(str, list2use))
    else:
        raise TypeError("Input list2use must be a list")
    return res
