"""
Nozomi
Time Module
author: hugh@blinkybeach.com
"""
from nozomi.data.codable import Codable
from nozomi.http.parseable_data import ParseableData
from nozomi.errors.bad_request import BadRequest
from datetime import timedelta
from datetime import datetime
from typing import TypeVar, Type, Any, Optional
from nozomi.temporal.tz_utc import UTC

T = TypeVar('T', bound='NozomiTime')


class NozomiTime(datetime, Codable):

    _DB_FORMAT_STRING = '%Y-%m-%d %H:%M:%S.%f'
    _NO_MS_FORMAT = '%Y-%m-%d %H:%M:%S'

    @classmethod
    def decode(cls: Type[T], data: Any) -> T:

        assert isinstance(data, str)
        if '+' in data:
            parsable = data.split('+')[0]
        else:
            if '-' in data.split(':')[2]:
                parsable = data[:-6]
            else:
                parsable = data
        parsable = parsable.replace('T', ' ')
        parsable = parsable.replace('_', ' ')
        try:
            time = cls.strptime(parsable, cls._DB_FORMAT_STRING)
        except ValueError:
            time = cls.strptime(parsable, cls._NO_MS_FORMAT)
        decoded = cls(
            year=time.year,
            month=time.month,
            day=time.day,
            hour=time.hour,
            minute=time.minute,
            second=time.second,
            microsecond=time.microsecond,
            tzinfo=UTC
        )

        return decoded

    def encode(self) -> str:
        return self.strftime(self._DB_FORMAT_STRING)

    @classmethod
    def utcnow(cls: Type[T]) -> T:
        time = datetime.utcnow()
        return cls._from_datetime(time.replace(tzinfo=UTC))

    @classmethod
    def from_unix_timestamp(cls: Type[T], timestamp: int) -> T:
        time = datetime.fromtimestamp(timestamp)
        return cls._from_datetime(time.replace(tzinfo=UTC))

    @classmethod
    def in_seconds_from_now(cls: Type[T], seconds: int) -> T:
        time = datetime.utcnow() + timedelta(seconds=seconds)
        return cls._from_datetime(time.replace(tzinfo=UTC))

    @classmethod
    def in_minutes_from_now(cls: Type[T], minutes: int) -> T:
        time = datetime.utcnow() + timedelta(minutes=minutes)
        return cls._from_datetime(time.replace(tzinfo=UTC))

    @classmethod
    def in_days_from_now(cls: Type[T], days: int) -> T:
        time = datetime.utcnow() + timedelta(days=days)
        return cls._from_datetime(time.replace(tzinfo=UTC))

    @classmethod
    def _from_datetime(cls: Type[T], time: datetime) -> T:
        return cls(
            year=time.year,
            month=time.month,
            day=time.day,
            hour=time.hour,
            minute=time.minute,
            second=time.second,
            microsecond=time.microsecond,
            tzinfo=time.tzinfo
        )

    @classmethod
    def strptime(cls: Type[T], timestring: str, timeformat: str) -> T:
        time = datetime.strptime(timestring, timeformat)
        return cls._from_datetime(time)

    @classmethod
    def strptime_utc(cls: Type[T], timestring: str, timeformat: str) -> T:
        time = datetime.strptime(timestring, timeformat)
        utc_time = time.replace(tzinfo=UTC)
        return cls._from_datetime(utc_time)

    @classmethod
    def from_request(
        cls: Type[T],
        data: ParseableData,
        key: str
    ) -> T:

        time = cls.optionally_from_request(data, key)
        if time is None:
            raise BadRequest('Supply a time, in format {f}, under key \
{k}'.format(f=cls._NO_MS_FORMAT, k=key))
        return time

    @classmethod
    def optionally_from_request(
        cls: Type[T],
        data: ParseableData,
        key: str
    ) -> Optional[T]:

        raw_time = data.optionally_parse_string(key, allow_whitespace=True)
        if raw_time is None:
            return None
        try:
            time = cls.decode(raw_time)
        except ValueError:
            raise BadRequest('Time must be in the format {f}'.format(
                f=cls._NO_MS_FORMAT
            ))
        return time
