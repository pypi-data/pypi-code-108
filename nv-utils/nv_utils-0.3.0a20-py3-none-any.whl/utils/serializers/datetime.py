"""Functions to format datetime objects."""

# For string parsers see nv.utils.parsers.string.datetime, which do the opposite


from datetime import datetime, date, time


__ALL__ = ["format_duration", "format_iso_duration", "format_iso_time", "format_iso_date", "format_iso_datetime"]


def split_delta(delta):
    days = delta.days
    hours, minutes = divmod(delta.seconds, 60 * 60)
    minutes, seconds = divmod(minutes, 60)
    microseconds = delta.microseconds
    return days, hours, minutes, seconds, microseconds


def format_duration(delta):
    days, hours, minutes, seconds, microseconds = split_delta(delta)
    return f"{days} {hours:02d}:{minutes:02d}:{seconds:02d}.{microseconds:06d}"


def format_iso_duration(delta, use_weeks=False, shorten=True):
    days, hours, minutes, seconds, microseconds = split_delta(delta)

    if use_weeks:
        weeks, days = divmod(days, 7)
        header = f"P{weeks}W{days}D"
    else:
        header = f"P{days}D"

    if not shorten or microseconds > 0:
        tail = f"T{hours:02d}:{minutes:02d}:{seconds:02d}.{microseconds:06d}"
    elif seconds > 0:
        tail = f"T{hours:02d}:{minutes:02d}:{seconds:02d}"
    elif minutes > 0:
        tail = f"T{hours:02d}:{minutes:02d}"
    elif hours > 0:
        tail = f"T{hours:02d}"
    else:
        tail = ""

    return f"{header}{tail}"


def format_iso_datetime(dt: datetime):
    return dt.isoformat().replace('+00:00', 'Z')


def format_iso_date(d: date):
    return d.isoformat()


def format_iso_time(t: time):
    return t.isoformat().replace('+00:00', 'Z')
