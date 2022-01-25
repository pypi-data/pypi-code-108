import sys
import typing
from dataclasses import dataclass
from datetime import datetime, date, time, timedelta, timezone

from expyct.base import Equals, MapBefore, Satisfies, Optional, BaseMatcher

if (3, 6) <= sys.version_info < (3, 7):
    # fromisoformat only became available in 3.7
    # See backport https://pypi.org/project/backports-datetime-fromisoformat/
    from backports.datetime_fromisoformat import MonkeyPatch

    MonkeyPatch.patch_fromisoformat()

T = typing.TypeVar("T")


@dataclass(repr=False, eq=False)
class AfterBefore(typing.Generic[T], BaseMatcher):
    """Mixin for matching a `date`, `time`, or `datetime` that takes place after, before, or on
    given date/time. In other words, it is inclusive on both sides.

    Arguments:
        after : object must occur after or exactly on given
        before : object must occur before or exactly on given
    """

    after: typing.Optional[T] = None
    before: typing.Optional[T] = None

    def __init__(
        self,
        after: typing.Optional[T] = None,
        before: typing.Optional[T] = None,
    ):
        """Mixin for matching a `date`, `time`, or `datetime` that takes place after, before, or on
        given date/time. In other words, it is inclusive on both sides.

            Args:
                after : object must occur after given
                before : object must occur before given
        """
        self.after = after
        self.before = before

    def _eq(self, other):
        if self.after is not None and not other >= self.after:
            return False
        if self.before is not None and not other <= self.before:
            return False
        return True


@dataclass(repr=False, eq=False)
class AfterBeforeStrict(typing.Generic[T], BaseMatcher):
    """Mixin for matching a `date`, `time`, or `datetime` that takes place after and/or before given
    date/time. In other words, it is exclusive on both sides."""

    after_strict: typing.Optional[T] = None
    before_strict: typing.Optional[T] = None

    def __init__(
        self,
        after_strict: typing.Optional[T] = None,
        before_strict: typing.Optional[T] = None,
    ):
        """Mixin for matching a `date`, `time`, or `datetime` that takes place after and/or before given
        date/time. In other words, it is exclusive on both sides.

            Args:
                after_strict : object must occur after given
                before_strict : object must occur before given
        """
        self.after_strict = after_strict
        self.before_strict = before_strict

    def _eq(self, other):
        if self.after_strict is not None and not other > self.after_strict:
            return False
        if self.before_strict is not None and not other < self.before_strict:
            return False
        return True


@dataclass(repr=False, eq=False)
class DateTime(
    Satisfies,
    AfterBeforeStrict[datetime],
    AfterBefore[datetime],
    Equals[datetime],
    Optional,
    MapBefore,
    BaseMatcher,
    datetime,
):
    """Match any object that is an instance of `datetime`."""

    def __new__(cls, *args, **kwargs):
        return datetime.__new__(cls, 1, 1, 1)

    def __init__(
        self,
        map_before: typing.Optional[typing.Callable] = None,
        optional: typing.Optional[bool] = None,
        equals: typing.Optional[typing.Any] = None,
        after: typing.Optional[datetime] = None,
        before: typing.Optional[datetime] = None,
        after_strict: typing.Optional[datetime] = None,
        before_strict: typing.Optional[datetime] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
    ):
        """Match any object that is an instance of `datetime`.

        Args:
            map_before : apply function before checking equality
            optional : whether `None` is allowed [default: `False`]
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            after : object must occur after or exactly on given
            before : object must occur before or exactly on given
            after_strict : object must occur after given
            before_strict : object must occur before given
            satisfies : object must satisfy predicate
        """
        self.map_before = map_before
        self.optional = optional
        self.equals = equals
        self.after = after
        self.before = before
        self.after_strict = after_strict
        self.before_strict = before_strict
        self.satisfies = satisfies

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        if other is None:
            return Optional._eq(self, other)
        if not type(other) == datetime:
            return False
        if not Equals._eq(self, other):
            return False
        if not AfterBefore._eq(self, other):
            return False
        if not AfterBeforeStrict._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        return True


@dataclass(repr=False, eq=False)
class DateTimeTz(
    Satisfies,
    AfterBeforeStrict[datetime],
    AfterBefore[datetime],
    Equals[datetime],
    Optional,
    MapBefore,
    BaseMatcher,
    datetime,
):
    """Match any object that is an instance of `datetime` and has timezone information (`tzinfo`).
    In other words, is a timestamp."""

    after: typing.Optional[typing.Union[datetime, timedelta]] = None  # type: ignore
    before: typing.Optional[typing.Union[datetime, timedelta]] = None  # type: ignore
    after_strict: typing.Optional[typing.Union[datetime, timedelta]] = None  # type: ignore
    before_strict: typing.Optional[typing.Union[datetime, timedelta]] = None  # type: ignore

    def __new__(cls, *args, **kwargs):
        return datetime.__new__(cls, 1, 1, 1)

    def __init__(
        self,
        map_before: typing.Optional[typing.Callable] = None,
        optional: typing.Optional[bool] = None,
        equals: typing.Optional[typing.Any] = None,
        after: typing.Optional[typing.Union[datetime, timedelta]] = None,
        before: typing.Optional[typing.Union[datetime, timedelta]] = None,
        after_strict: typing.Optional[typing.Union[datetime, timedelta]] = None,
        before_strict: typing.Optional[typing.Union[datetime, timedelta]] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
    ):
        """Match any object that is an instance of `datetime` and has timezone information (`tzinfo`).
        In other words, is a timestamp.

        Args:
            map_before : apply function before checking equality
            optional : whether `None` is allowed [default: `False`]
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            after : object must occur after or on given. If timedelta is given,
                then it is compared relative to when the assertion is run
            before : object must occur before or on given. If timedelta is given,
                then it is compared relative to when the assertion is run
            after_strict : object must occur after given
            before_strict : object must occur before given
            satisfies : object must satisfy predicate
        """
        self.map_before = map_before
        self.optional = optional
        self.equals = equals
        self.after = after
        self.before = before
        self.after_strict = after_strict
        self.before_strict = before_strict
        self.satisfies = satisfies

    after: typing.Optional[typing.Union[datetime, timedelta]] = None  # type: ignore
    before: typing.Optional[typing.Union[datetime, timedelta]] = None  # type: ignore
    after_strict: typing.Optional[typing.Union[datetime, timedelta]] = None  # type: ignore
    before_strict: typing.Optional[typing.Union[datetime, timedelta]] = None  # type: ignore

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        if other is None:
            return Optional._eq(self, other)
        if not type(other) == datetime:
            return False
        if other.tzinfo is None:
            return False
        if self.equals:
            if self.equals.tzinfo is None:
                raise ValueError("equals is missing tzinfo")
        if not Equals._eq(self, other):
            return False
        if self.before:
            self.before = DateTimeTz._handle_timedelta(self.before)
            if self.before.tzinfo is None:
                raise ValueError("before is missing tzinfo")
        if self.after:
            self.after = DateTimeTz._handle_timedelta(self.after)
            if self.after.tzinfo is None:
                raise ValueError("after is missing tzinfo")
        if not AfterBefore._eq(self, other):
            return False
        if self.before_strict:
            self.before_strict = DateTimeTz._handle_timedelta(self.before_strict)
            if self.before_strict.tzinfo is None:
                raise ValueError("before_strict is missing tzinfo")
        if self.after_strict:
            self.after_strict = DateTimeTz._handle_timedelta(self.after_strict)
            if self.after_strict.tzinfo is None:
                raise ValueError("after_strict is missing tzinfo")
        if not AfterBeforeStrict._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        return True

    @staticmethod
    def _handle_timedelta(
        bound: typing.Union[datetime, date, time, timedelta]
    ) -> typing.Union[datetime, date, time]:
        """When timedelta is passed, it is used as a time relative to when the assertion is
        executed."""

        if isinstance(bound, timedelta):
            return datetime.now().astimezone(timezone.utc) + bound
        else:
            return bound


@dataclass(repr=False, eq=False)
class Date(
    Satisfies,
    AfterBeforeStrict[date],
    AfterBefore[date],
    Equals[date],
    Optional,
    MapBefore,
    BaseMatcher,
    date,
):
    """Match any object that is an instance of `date`."""

    def __new__(cls, *args, **kwargs):
        return date.__new__(cls, 1, 1, 1)

    def __init__(
        self,
        map_before: typing.Optional[typing.Callable] = None,
        optional: typing.Optional[bool] = None,
        equals: typing.Optional[typing.Any] = None,
        after: typing.Optional[date] = None,
        before: typing.Optional[date] = None,
        after_strict: typing.Optional[date] = None,
        before_strict: typing.Optional[date] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
    ):
        """Match any object that is an instance of `date`.

        Args:
            map_before : apply function before checking equality
            optional : whether `None` is allowed
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            after : object must occur after or on given. If timedelta is given,
                then it is compared relative to when the assertion is run
            before : object must occur before or on given. If timedelta is given,
                then it is compared relative to when the assertion is run
            after_strict : object must occur after given
            before_strict : object must occur before given
            satisfies : object must satisfy predicate
        """
        self.map_before = map_before
        self.optional = optional
        self.equals = equals
        self.after = after
        self.before = before
        self.after_strict = after_strict
        self.before_strict = before_strict
        self.satisfies = satisfies

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        if other is None:
            return Optional._eq(self, other)
        if not type(other) == date:
            return False
        if not Equals._eq(self, other):
            return False
        if not AfterBefore._eq(self, other):
            return False
        if not AfterBeforeStrict._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        return True


@dataclass(repr=False, eq=False)
class Time(
    Satisfies,
    AfterBeforeStrict[time],
    AfterBefore[time],
    Equals[time],
    Optional,
    MapBefore,
    BaseMatcher,
    time,
):
    """Match any object that is an instance of `time`."""

    def __new__(cls, *args, **kwargs):
        return time.__new__(cls, 1, 1, 1)

    def __init__(
        self,
        map_before: typing.Optional[typing.Callable] = None,
        optional: typing.Optional[bool] = None,
        equals: typing.Optional[typing.Any] = None,
        after: typing.Optional[time] = None,
        before: typing.Optional[time] = None,
        after_strict: typing.Optional[time] = None,
        before_strict: typing.Optional[time] = None,
        satisfies: typing.Optional[typing.Callable[[typing.Any], bool]] = None,
    ):
        """Match any object that is an instance of `time`.

        Args:
            map_before : apply function before checking equality
            optional : whether `None` is allowed
            equals : object must equal exactly. This is useful together with
                `map_before` to check a value after applying a function
            after : object must occur after or on given. If timedelta is given,
                then it is compared relative to when the assertion is run
            before : object must occur before or on given. If timedelta is given,
                then it is compared relative to when the assertion is run
            after_strict : object must occur after given
            before_strict : object must occur before given
            satisfies : object must satisfy predicate
        """
        self.map_before = map_before
        self.optional = optional
        self.equals = equals
        self.after = after
        self.before = before
        self.after_strict = after_strict
        self.before_strict = before_strict
        self.satisfies = satisfies

    def _eq(self, other):
        try:
            other = MapBefore.map(self, other)
        except Exception:
            return False
        if other is None:
            return Optional._eq(self, other)
        if not type(other) == time:
            return False
        if not Equals._eq(self, other):
            return False
        if not AfterBefore._eq(self, other):
            return False
        if not AfterBeforeStrict._eq(self, other):
            return False
        if not Satisfies._eq(self, other):
            return False
        return True


def parse_isoformat(dt: str) -> typing.Union[date, time, datetime]:
    """Parse a ISO8601-formatted string as a `date`, `datetime` or `datetime` object.

        This will depend on the amount of information that is given.

    Args:
        dt : the date/time string to parse
    """
    if isinstance(dt, str):
        try:
            return date.fromisoformat(dt)  # type: ignore
        except ValueError:
            try:
                return time.fromisoformat(dt)  # type: ignore
            except ValueError:
                if dt.endswith("Z"):
                    dt = dt[:-1] + "+00:00"
                return datetime.fromisoformat(dt).astimezone(timezone.utc)  # type: ignore
    raise ValueError("Only str is allowed as input")


#: Any instance of `datetime`
ANY_DATETIME = DateTime()
#: Any instance of `date`
ANY_DATE = Date()
#: Any instance `time`
ANY_TIME = Time()

#: Any string that can be parsed as `datetime` using the ISO8601 format
ANY_DATETIME_ISO = DateTime(map_before=parse_isoformat)
#: Any string that can be parsed as `date` using the ISO8601 format
ANY_DATE_ISO = Date(map_before=parse_isoformat)
#: Any string that can be parsed as `time` using the ISO8601 format
ANY_TIME_ISO = Time(map_before=parse_isoformat)

#: Any timestamp occurring during the last second
LAST_SECOND = DateTimeTz(after=timedelta(seconds=-1), before=timedelta())
#: Any timestamp occurring during the last 60 seconds
LAST_MINUTE = DateTimeTz(after=timedelta(minutes=-1), before=timedelta())
#: Any timestamp occurring during the last 60 minutes
LAST_HOUR = DateTimeTz(after=timedelta(hours=-1), before=timedelta())
#: Any timestamp occurring during the last 24 hours
LAST_DAY = DateTimeTz(after=timedelta(days=-1), before=timedelta())
#: Any timestamp occurring during the last 7 days
LAST_WEEK = DateTimeTz(after=timedelta(weeks=-1), before=timedelta())
#: Any timestamp occurring during the last 365 days
LAST_YEAR = DateTimeTz(after=timedelta(days=-365), before=timedelta())
#: Any timestamp occurring during the last second, parsed from ISO8601 string
LAST_SECOND_ISO = DateTimeTz(
    after=timedelta(seconds=-1), before=timedelta(), map_before=parse_isoformat
)
#: Any timestamp occurring during the last 60 seconds, parsed from ISO8601 string
LAST_MINUTE_ISO = DateTimeTz(
    after=timedelta(minutes=-1), before=timedelta(), map_before=parse_isoformat
)
#: Any timestamp occurring during the last 60 minutes, parsed from ISO8601 string
LAST_HOUR_ISO = DateTimeTz(
    after=timedelta(hours=-1), before=timedelta(), map_before=parse_isoformat
)
#: Any timestamp occurring during the last 24 hours, parsed from ISO8601 string
LAST_DAY_ISO = DateTimeTz(after=timedelta(days=-1), before=timedelta(), map_before=parse_isoformat)
#: Any timestamp occurring during the last 7 days, parsed from ISO8601 string
LAST_WEEK_ISO = DateTimeTz(
    after=timedelta(weeks=-1), before=timedelta(), map_before=parse_isoformat
)
#: Any timestamp occurring during the last 365 days, parsed from ISO8601 string
LAST_YEAR_ISO = DateTimeTz(
    after=timedelta(days=-365), before=timedelta(), map_before=parse_isoformat
)


def floor_second(dt: datetime):
    return dt.replace(microsecond=0)


def floor_minute(dt: datetime):
    return dt.replace(second=0, microsecond=0)


def floor_hour(dt: datetime):
    return dt.replace(minute=0, second=0, microsecond=0)


def floor_day(dt: datetime):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def floor_year(dt: datetime):
    return dt.replace(month=0, day=0, hour=0, minute=0, second=0, microsecond=0)


#: Any timestamp occurring in the current second
THIS_SECOND = DateTimeTz(
    after_strict=floor_second(datetime.now()) - timedelta(seconds=1),
    before_strict=floor_second(datetime.now()) + timedelta(seconds=1),
)
#: Any timestamp occurring in the current minute
THIS_MINUTE = DateTimeTz(
    after_strict=floor_minute(datetime.now()) - timedelta(minutes=1),
    before_strict=floor_minute(datetime.now()) + timedelta(minutes=1),
)
#: Any timestamp occurring in the current hour
THIS_HOUR = DateTimeTz(
    after_strict=floor_hour(datetime.now()) - timedelta(hours=1),
    before_strict=floor_hour(datetime.now()) + timedelta(hours=1),
)
#: Any timestamp occurring on the current day
THIS_DAY = DateTimeTz(
    after_strict=floor_day(datetime.now()) - timedelta(days=1),
    before_strict=floor_day(datetime.now()) + timedelta(days=1),
)
#: The same as THIS_DAY
TODAY = THIS_DAY

#: Any timestamp occurring on the current day, parsed from ISO8601 string
THIS_DAY_ISO = DateTimeTz(
    after_strict=floor_day(datetime.now()) - timedelta(days=1),
    before_strict=floor_day(datetime.now()) + timedelta(days=1),
    map_before=parse_isoformat,
)
#: The same as THIS_DAY_ISO
TODAY_ISO = THIS_DAY_ISO
