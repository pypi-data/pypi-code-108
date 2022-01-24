import pytz

from typing import Optional

from datetime import datetime
from pytz import reference


class DKDateHelper:
    def __init__(self) -> None:
        pass

    @staticmethod
    def format_timestamp(ts: Optional[int]) -> str:
        if ts is None:
            return "Not available - None"
        if not isinstance(ts, int):
            return f"Not available - bad format: {ts}"
        to_zone = reference.LocalTimezone()
        utc_datetime = datetime.utcfromtimestamp(ts / 1000.0)
        locale_datetime = pytz.utc.localize(utc_datetime, is_dst=None).astimezone(to_zone)
        return locale_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")

    @staticmethod
    def format_timing(t: Optional[int]) -> str:
        if t is None:
            return "Not available - None"
        if not isinstance(t, int):
            return f"Not available - bad format: {t}"
        secs = int((t / 1000) % 60)
        mins = int((t / (1000 * 60)) % 60)
        hours = int(t / (1000 * 60 * 60))
        return f"{hours}:{mins:02}:{secs:02}"
