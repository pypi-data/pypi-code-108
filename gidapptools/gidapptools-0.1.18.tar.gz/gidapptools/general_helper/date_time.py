"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from enum import Enum
from pathlib import Path
from datetime import datetime, timezone, timedelta
from functools import total_ordering

# * Third Party Imports --------------------------------------------------------------------------------->
import attr

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.errors import DateTimeFrameTimezoneError

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


# def seconds2human()


class DatetimeFmt(str, Enum):
    STANDARD = "%Y-%m-%d %H:%M:%S"
    FILE = "%Y-%m-%d_%H-%M-%S"
    LOCAL = "%x %X"

    STANDARD_TZ = "%Y-%m-%d %H:%M:%S %Z"
    FILE_TZ = "%Y-%m-%d_%H-%M-%S_%Z"
    LOCAL_TZ = "%x %X %Z"

    def strf(self, date_time: datetime) -> str:
        non_tz_fmt = self if not self.name.endswith('_TZ') else getattr(self, self.name.removesuffix('_TZ'))
        tz_fmt = self if self.name.endswith('_TZ') else getattr(self, self.name + '_TZ')
        if date_time.tzinfo is None:
            return date_time.strftime(non_tz_fmt)
        return date_time.strftime(tz_fmt)


# class NamedTimezone:
#     LOCAL = get_localzone()
#     UTC = timezone.utc
#     GMT = timezone(offset=timedelta(hours=0), name='GMT')
#     CET = pytz.timezone('CET')
#     CST = pytz.timezone('America/Winnipeg')

#     @classmethod
#     def get(cls, name: str, default: Any = None) -> Optional[tzinfo]:
#         mod_name = name.upper().strip()
#         return getattr(cls, mod_name, default)


def get_aware_now(tz: timezone) -> datetime:
    return datetime.now(tz=tz)


def get_utc_now() -> datetime:
    return get_aware_now(tz=timezone.utc)


def _validate_date_time_frame_tzinfo(instance: "DateTimeFrame", attribute: attr.Attribute, value: datetime):
    if instance.start.tzinfo is None or instance.end.tzinfo is None:
        raise DateTimeFrameTimezoneError(instance, instance.start.tzinfo, instance.end.tzinfo, 'start time and end time need to be timezone aware')
    if instance.start.tzinfo != instance.end.tzinfo:
        raise DateTimeFrameTimezoneError(instance, instance.start.tzinfo, instance.end.tzinfo, 'start time and end time do not have the same timezone')


@attr.s(auto_attribs=True, auto_detect=True, frozen=True)
@total_ordering
class DateTimeFrame:
    start: datetime = attr.ib(validator=_validate_date_time_frame_tzinfo)
    end: datetime = attr.ib(validator=_validate_date_time_frame_tzinfo)

    @property
    def delta(self) -> timedelta:
        return self.end - self.start

    @property
    def tzinfo(self) -> timezone:
        return self.start.tzinfo

    def __eq__(self, other: object) -> bool:
        if isinstance(other, datetime):
            return self.start <= other <= self.end
        if isinstance(other, self.__class__):
            return self.start == other.start and self.end == other.end
        if isinstance(other, timedelta):
            return self.delta == other
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, datetime):
            return self.start < other
        if isinstance(other, self.__class__):
            return self.end < other.start
        if isinstance(other, timedelta):
            return self.delta < other
        return NotImplemented

    def __contains__(self, other: object) -> bool:
        if isinstance(other, datetime):
            return self.start <= other <= self.end
        return NotImplemented

    def __str__(self) -> str:
        return f"{self.start.isoformat()} until {self.end.isoformat()}"

    def __hash__(self) -> int:
        return hash(self.start) + hash(self.end) + hash(self.delta)
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
