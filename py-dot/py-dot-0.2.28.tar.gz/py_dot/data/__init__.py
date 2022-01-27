from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import Type, Union, List, Tuple, Dict

from py_dot.core.date import Period, DateParts


class SummaryTimeUnit:
    year = 'year'
    month = 'month'
    date = 'date'
    hour = 'hour'
    minute = 'minute'
    second = 'second'

    def __init__(
        self,
        year='year',
        month='month',
        date='date',
        hour='hour',
        minute='minute',
        second='second',
        default=None
    ):
        self.year = year
        self.month = month
        self.date = date
        self.hour = hour
        self.minute = minute
        self.second = second
        self.default = default


def get_summary_unit(
    period: Period,
    unit: Union[SummaryTimeUnit, Type[SummaryTimeUnit]] = SummaryTimeUnit,
    year_days: int = 365,
    month_days: int = 30,
    year_from: int = 3,
    month_from: int = 6,
    date_from: int = 3,
    hour_from: int = 28,
    minute_from: int = 3599
) -> Tuple[any, int, int]:
    duration_time = period.duration_time

    begin = DataSummaryTimeDigits(period.begin)
    end = DataSummaryTimeDigits(period.end)

    days = ceil(duration_time / 86400)

    if unit.year is not None:
        if days >= year_days * year_from:
            return unit.year, begin.y, end.y

    if unit.month is not None:
        if days >= month_days * month_from:
            return unit.month, begin.ym, end.ym

    if unit.date is not None:
        if days >= date_from:
            return unit.date, begin.ymd, end.ymd

    if unit.hour is not None:
        if days >= hour_from:
            return unit.hour, begin.ymdh, end.ymdh

    if unit.minute is not None:
        if duration_time >= minute_from:
            return unit.minute, begin.ymdhi, end.ymdhi

    return unit.default, period.begin, period.end


class DataSummaryTimeDigits:
    y: int
    ym: int
    ymd: int
    ymdh: int
    ymdhi: int

    def __init__(self, time: datetime = None, parts: DateParts = None):
        if parts is None:
            if time is None:
                raise ValueError('time or parts Arguments is Required.')

            parts = DateParts(time)

        y = parts.y
        m = parts.m
        d = parts.d
        h = parts.h
        i = parts.i

        ym = y + m
        ymd = ym + d
        ymdh = ymd + h
        ymdhi = ymdh + i

        self.y = int(y)
        self.ym = int(ym)
        self.ymd = int(ymd)
        self.ymdh = int(ymdh)
        self.ymdhi = int(ymdhi)

    def get(self, unit: str):
        pass


@dataclass
class DataSummaryTimeStrings:
    y: str
    ym: str
    ymd: str
    ymdh: str
    ymdhi: str

    def __init__(self, time: datetime = None, parts: DateParts = None):
        if parts is None:
            if time is None:
                raise ValueError('time or parts Arguments is Required.')

            parts = DateParts(time)

        y, m, d, h, i = parts

        ym = y + '-' + m
        ymd = ym + '-' + d
        ymdh = ymd + ' ' + h
        ymdhi = ymdh + ':' + i

        self.y = y
        self.ym = ym
        self.ymd = ymd
        self.ymdh = ymdh
        self.ymdhi = ymdhi


class DataSummaryTimes:
    digits: DataSummaryTimeDigits
    strings: DataSummaryTimeStrings

    def __init__(self, time: datetime):
        parts = DateParts(time)

        self.digits = DataSummaryTimeDigits(parts=parts)
        self.strings = DataSummaryTimeStrings(parts=parts)


def data_split_list(
    items: List[Union[Tuple, List]],
    key_index=0,
    date_index=1,
    value_index=2,
    header: Tuple[str, str] = None
) -> Dict:
    result = {}

    for item in items:
        key = item[key_index]
        date = item[date_index]
        value = item[value_index]

        item = (date, value)
        if key in result:
            result[key].append(item)
        else:
            if header:
                result[key] = [header, item]
                continue
            result[key] = [item]

    return result
