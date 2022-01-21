from __future__ import annotations

import datetime
import enum
from dataclasses import dataclass
from typing import Optional

from .helpers import Atomic


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
    format = DateFormat.datetime.from_datetime


@dataclass
class Date(Atomic):
    format = DateFormat.date.from_datetime


@dataclass
class CharacterString(Atomic):
    pass


@dataclass
class TM_PeriodDuration:
    ...
