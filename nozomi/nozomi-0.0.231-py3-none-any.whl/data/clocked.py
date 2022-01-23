"""
Nozomi
Clocked Module
author: hugh@blinkybeach.com
"""
from nozomi.temporal.time import NozomiTime
from nozomi.ancillary.immutable import Immutable
from nozomi.temporal.tz_utc import TimeZoneUTC
from datetime import timedelta
from typing import Optional


class Clocked:
    """
    Abstract class providing an interface for classes that wish to measure
    the speed of their initialisation.
    """

    query_start: NozomiTime = NotImplementedError
    query_time: timedelta = Immutable(
        lambda s: s._clocked_format_execution_time()
    )
    query_time_microseconds: int = Immutable(
        lambda s: int(
            s.query_time.seconds * 1000 + s.query_time.microseconds / 1000
        )
    )

    _clocked_query_end: Optional[NozomiTime] = None

    @classmethod
    def start_query_clock(self) -> NozomiTime:
        return NozomiTime.utcnow().replace(tzinfo=TimeZoneUTC())

    def mark_initialisation_ended(
        self,
        end_time: Optional[NozomiTime] = None
    ) -> None:
        if end_time is None:
            end_time = NozomiTime.utcnow()
        self._clocked_query_end = end_time.replace(
            tzinfo=TimeZoneUTC()
        )
        return

    def _clocked_format_execution_time(self) -> int:
        query_time = self._clocked_compute_execution_time()
        seconds = query_time.seconds
        microseconds = query_time.microseconds
        return int(((seconds) * 1000 + microseconds) / 1000)

    def _clocked_compute_execution_time(self) -> timedelta:
        if not isinstance(self.query_start, NozomiTime):
            raise NotImplementedError('Implement .query_start')
        if not isinstance(self._clocked_query_end, NozomiTime):
            raise NotImplementedError('Call .mark_initialisation_ended()')
        return self._clocked_query_end - self.query_start
