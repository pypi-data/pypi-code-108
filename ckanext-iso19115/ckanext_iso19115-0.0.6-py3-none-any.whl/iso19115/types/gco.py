from __future__ import annotations

import datetime
import enum
from dataclasses import dataclass
from typing import Any

from .base import Atomic


class DateFormat(enum.Enum):
    datetime = "%Y-%m-%dT%H:%M:%S"
    date = "%Y-%m-%d"
    gYearMonth = "%Y-%m"
    gYear = "%Y"

    def key(self):
        if self is DateFormat.datetime:
            return "gco:DateTime"
        return "gco:Date"

    def from_datetime(self, dt: datetime.date):
        return dt.strftime(self.value)


@dataclass
class DateTime(Atomic):
    value: datetime.datetime
    format = DateFormat.datetime.from_datetime


@dataclass
class Date(Atomic):
    value: datetime.date
    format = DateFormat.date.from_datetime


@dataclass
class CharacterString(Atomic):
    value: str


@dataclass
class Real(Atomic):
    value: float


@dataclass
class Measure(Atomic):
    value: float


@dataclass
class Integer(Atomic):
    value: int


@dataclass
class Boolean(Atomic):
    value: bool


@dataclass
class TM_PeriodDuration:
    ...


@dataclass
class Record:
    value: Any


@dataclass
class RecordType:
    ...


@dataclass
class MemberName:
    ...


@dataclass
class ScopedName:
    ...
