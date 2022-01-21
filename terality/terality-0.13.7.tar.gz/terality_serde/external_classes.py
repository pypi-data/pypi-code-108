import re
from abc import ABC, abstractmethod
import base64
from dataclasses import dataclass
from datetime import datetime, time, timedelta, date
from io import BytesIO
from pathlib import Path, PosixPath
from re import Pattern
from typing import Any, List, Optional, Set, Type, Union

import numpy as np
import pandas as pd
from pandas.tseries.offsets import (
    Nano,
    Micro,
    Milli,
    Easter,
    FY5253,
    BusinessHour,
    CustomBusinessDay,
    Second,
    Minute,
    Hour,
    Day,
    BusinessDay,
    Week,
    SemiMonthBegin,
    SemiMonthEnd,
    MonthBegin,
    MonthEnd,
    BMonthEnd,
    BMonthBegin,
    WeekOfMonth,
    LastWeekOfMonth,
    BQuarterBegin,
    BQuarterEnd,
    QuarterBegin,
    QuarterEnd,
    YearBegin,
    YearEnd,
    BYearBegin,
    BYearEnd,
)

from dateutil.parser import ParserError

# noinspection PyProtectedMember
from pandas._libs import missing, OutOfBoundsDatetime, tslibs
import pyarrow


@dataclass  # type: ignore
class ExternalTypeSerializer(ABC):
    class_: type

    @property
    def class_name(self) -> str:
        return f"{self.class_.__module__}.{self.class_.__name__}"

    @abstractmethod
    def to_json(self, value: Any) -> dict:
        pass

    @abstractmethod
    def from_json(self, **kwargs):
        pass


@dataclass
class TupleSerde(ExternalTypeSerializer):
    class_: type = tuple

    def to_json(self, value: tuple) -> dict:
        return {"as_list": list(value)}

    def from_json(self, as_list: list) -> tuple:  # type: ignore
        return tuple(as_list)


@dataclass
class OffsetsGenericSerde(ExternalTypeSerializer):
    class_: type
    useful_attributes: List[str]

    def to_json(self, value) -> dict:
        return {attribute: getattr(value, attribute) for attribute in self.useful_attributes}

    def from_json(self, **kwargs):
        return self.class_(**kwargs)


@dataclass
class DictSerde(ExternalTypeSerializer):
    """
    Serialize dict with non-strings keys as json only handle strings keys.
    """

    class_: type = dict

    def to_json(self, value: dict) -> dict:
        return {"keys": list(value.keys()), "values": list(value.values())}

    def from_json(self, keys: list, values: list) -> dict:  # type: ignore
        assert len(keys) == len(values)
        return dict(zip(keys, values))


@dataclass
class SetSerde(ExternalTypeSerializer):
    """
    Serialize dict with non-strings keys as json only handle strings keys.
    """

    class_: type = set

    def to_json(self, value: set) -> dict:
        return {"values": list(value)}

    def from_json(self, values: list) -> set:  # type: ignore
        return set(values)


@dataclass
class RangeSerde(ExternalTypeSerializer):
    class_: type = range

    def to_json(self, value: range) -> dict:
        return {"as_list": [value.start, value.stop, value.step]}

    def from_json(self, as_list: list) -> range:  # type: ignore
        return range(*as_list)


@dataclass
class SliceSerde(ExternalTypeSerializer):
    class_: type = slice

    def to_json(self, value: slice) -> dict:
        return {"as_list": [value.start, value.stop, value.step]}

    def from_json(self, as_list: list) -> slice:  # type: ignore
        return slice(*as_list)


@dataclass
class TimeSerde(ExternalTypeSerializer):
    class_: type = time

    def to_json(self, value: time) -> dict:
        return {"isoformat": value.isoformat()}

    def from_json(self, isoformat: str) -> time:  # type: ignore
        return time.fromisoformat(isoformat)


@dataclass
class DateSerde(ExternalTypeSerializer):
    class_: type = date

    def to_json(self, value: date) -> dict:
        return {"isoformat": value.isoformat()}

    def from_json(self, isoformat: str) -> date:  # type: ignore
        return date.fromisoformat(isoformat)


@dataclass
class DateTimeSerde(ExternalTypeSerializer):
    class_: type = datetime

    def to_json(self, value: datetime) -> dict:
        return {"isoformat": value.isoformat()}

    def from_json(self, isoformat: str) -> datetime:  # type: ignore
        return datetime.fromisoformat(isoformat)


@dataclass
class TimeStampSerde(ExternalTypeSerializer):
    """
    Pandas does not handle the timezones in isoformat, so we have to manually
    remove/put back timezones in serde...
    """

    class_: type = pd.Timestamp

    def to_json(self, value: pd.Timestamp) -> dict:
        timezone = None if value.tz is None else str(value.tz)
        if timezone is not None:
            value = value.astimezone(None)
        return {"isoformat": value.value, "timezone": timezone}

    def from_json(self, isoformat: int, timezone: Optional[str]) -> pd.Timestamp:  # type: ignore
        timestamp = pd.to_datetime(isoformat)
        # timestamp = pd.Timestamp.fromisoformat(isoformat)
        if timezone is not None:
            timestamp = timestamp.tz_localize("UTC").astimezone(timezone)
        return timestamp


@dataclass
class PeriodSerde(ExternalTypeSerializer):
    """
    We have a dtype to handle array of Period, but we need this serde to pass scalar as function parameter.
    This serde is tested in df_setitem.
    """

    class_: type = pd.Period

    def to_json(self, value: pd.Period) -> dict:
        isoformat = value.to_timestamp().value
        return {"isoformat": isoformat, "freq": value.freq.name}

    def from_json(self, isoformat: int, freq: str) -> pd.Period:  # type: ignore
        timestamp = pd.to_datetime(isoformat)
        return pd.Period(
            year=timestamp.year,
            month=timestamp.month,
            day=timestamp.day,
            hour=timestamp.hour,
            minute=timestamp.minute,
            second=timestamp.second,
            freq=freq,
        )


@dataclass
class IntervalSerde(ExternalTypeSerializer):
    """
    We have a dtype to handle array of Interval, but we need this serde to pass scalar as function parameter.
    This serde is tested in df_setitem.
    """

    class_: type = pd.Interval

    # TODO Handle non-builtin scalar for left/right
    def to_json(self, value: pd.Interval) -> dict:
        return {"left": value.left, "right": value.right, "closed": value.closed}

    def from_json(self, left, right, closed: str) -> pd.Interval:  # type: ignore
        return pd.Interval(left=left, right=right, closed=closed)


@dataclass
class TimedeltaSerde(ExternalTypeSerializer):
    class_: type = pd.Timedelta

    def to_json(self, value: pd.Timedelta) -> dict:
        return {"value_ns": value.value}

    def from_json(self, value_ns: int) -> Union[pd.Timedelta, type(pd.NaT)]:  # type: ignore
        return pd.Timedelta(value=value_ns, unit="ns")


@dataclass
class PyTimedeltaSerde(ExternalTypeSerializer):
    class_: type = timedelta

    def to_json(self, value: timedelta) -> dict:
        return {"days": value.days, "seconds": value.seconds, "microseconds": value.microseconds}

    def from_json(self, days: int, seconds: int, microseconds: int) -> timedelta:  # type: ignore
        return timedelta(days=days, seconds=seconds, microseconds=microseconds)


@dataclass
class PathSerde(ExternalTypeSerializer):
    class_: type = PosixPath

    def to_json(self, value: Path) -> dict:
        return {"path_as_str": str(value)}

    def from_json(self, path_as_str: str) -> Path:  # type: ignore
        return Path(path_as_str)


@dataclass
class BytesSerde(ExternalTypeSerializer):
    class_: type = bytes

    def to_json(self, value: bytes) -> dict:
        # ascii85 may be more space-efficient, but it includes many characters that would need to be escaped
        # when sent over HTTP. Overall, let's stick to something that doesn't include weird characters,
        # and we'll revisit this if performance becomes an issue.
        return {"bytes_base64": base64.b64encode(value).decode("utf-8")}

    def from_json(self, bytes_base64: bytes) -> bytes:  # type: ignore
        return base64.b64decode(bytes_base64)


@dataclass
class NumpyDType(ExternalTypeSerializer):
    class_: type = np.dtype

    def to_json(self, value: np.dtype) -> dict:
        return {"dtype_name": value.name}

    def from_json(self, dtype_name: str) -> np.dtype:  # type: ignore
        return np.dtype(dtype_name)


@dataclass
class NumpyArray(ExternalTypeSerializer):
    class_: type = np.ndarray

    def to_json(self, value: np.ndarray) -> dict:
        return {
            "buffer": base64.b64encode(value.tobytes()).decode("ascii"),
            "dtype": str(value.dtype),
        }

    def from_json(self, buffer: str, dtype: str) -> np.number:  # type: ignore
        return np.frombuffer(base64.b64decode(buffer.encode("ascii")), dtype=dtype)


@dataclass
class NumpyScalarSerde(ExternalTypeSerializer):
    def to_json(self, value: np.number) -> dict:
        return {"value": value.item()}

    def from_json(self, value: str) -> np.number:  # type: ignore
        return self.class_(value)


numpy_scalars = [
    NumpyScalarSerde(np_scalar_type)
    for np_scalar_type in [
        np.bool_,
        np.uint8,
        np.uint16,
        np.uint32,
        np.uint64,
        np.int8,
        np.int16,
        np.int32,
        np.int64,
        np.float64,
    ]
]


@dataclass
class NumpyF32Serde(ExternalTypeSerializer):
    class_: type = np.float32

    def to_json(self, value: np.float32) -> dict:
        bytes_io = BytesIO()
        # noinspection PyTypeChecker
        np.save(bytes_io, value)
        o_bytes = bytes_io.getvalue()
        o_str = base64.b64encode(o_bytes).decode()
        return {"float_as_array": o_str}

    def from_json(self, float_as_array: str) -> np.float32:  # type: ignore
        bytes_io = BytesIO(base64.b64decode(float_as_array.encode()))
        # Numpy signature does  not list all variants
        # noinspection PyTypeChecker
        return np.load(bytes_io).flatten()[0]


@dataclass
class NumpyDateTime64Serde(ExternalTypeSerializer):
    class_: type = np.datetime64

    def to_json(self, value: np.datetime64) -> dict:
        # This is horrible, best bet seems to go through pandas to manage to serde them:
        # https://stackoverflow.com/questions/13703720/converting-between-datetime-timestamp-and-datetime64
        return {"datetime_as_isoformat": pd.Timestamp(value).isoformat()}

    def from_json(self, datetime_as_isoformat: str) -> np.datetime64:  # type: ignore
        return np.datetime64(datetime_as_isoformat)


@dataclass
class NumpyBusDayCalendarSerde(ExternalTypeSerializer):
    class_: type = np.busdaycalendar

    def to_json(self, value: np.busdaycalendar) -> dict:
        return {"weekmask": value.weekmask, "holidays": value.holidays}

    def from_json(  # type: ignore
        self, weekmask: Union[str, List[bool]], holidays: List[np.datetime64]
    ) -> np.busdaycalendar:
        return np.busdaycalendar(weekmask, holidays)


@dataclass
class PandasMissingSerde(ExternalTypeSerializer):
    value: Any

    def to_json(self, value: np.number) -> dict:
        return {}

    def from_json(self) -> np.number:  # type: ignore
        return self.value


@dataclass
class PandasNASerde(PandasMissingSerde):
    class_: type = missing.NAType  # pylint: disable=c-extension-no-member
    value: Any = pd.NA


@dataclass
class PandasNaTSerde(PandasMissingSerde):
    class_: type = tslibs.NaTType
    value: Any = pd.NaT


@dataclass
class PyarrowDataType(ExternalTypeSerializer):
    class_: type = pyarrow.DataType

    _mapping = {
        data_type.id: data_type
        for data_type in [
            pyarrow.null(),
            pyarrow.string(),
            pyarrow.date32(),
            pyarrow.date64(),
        ]
    }

    def to_json(self, value: pyarrow.DataType) -> dict:
        return {"value": value.id}

    def from_json(self, value: str) -> type:  # type: ignore
        return self._mapping[value]


@dataclass
class PandasDType(ExternalTypeSerializer):
    class_: type = pd.api.extensions.ExtensionDtype

    def to_json(self, value: pd.api.extensions.ExtensionDtype) -> dict:
        return {"dtype_name": value.name}

    def from_json(self, dtype_name: str) -> np.dtype:  # type: ignore
        return pd.api.types.pandas_dtype(dtype_name)


@dataclass
class PandasCategoricalSerde(ExternalTypeSerializer):
    class_: type = pd.Categorical

    def to_json(self, value: pd.Categorical) -> dict:
        return {
            "codes": value.codes.tolist(),
            "categories": value.categories.tolist(),
            "ordered": value.ordered,
        }

    def from_json(self, codes: str, categories, ordered: bool) -> pd.Categorical:  # type: ignore
        return pd.Categorical.from_codes(codes=codes, categories=categories, ordered=ordered)


@dataclass
class PandasIntervalSerde(ExternalTypeSerializer):
    class_: type = pd.Interval

    def to_json(self, value: pd.Interval) -> dict:
        return {"left": value.left, "right": value.right, "closed": value.closed}

    def from_json(self, left: Any, right: Any, closed: str) -> pd.Interval:  # type: ignore
        return pd.Interval(left=left, right=right, closed=closed)


@dataclass
class RegexSerde(ExternalTypeSerializer):
    class_: type = Pattern

    def to_json(self, regex: Pattern) -> dict:
        return {"pattern": regex.pattern}

    def from_json(self, pattern: str) -> Pattern:  # type: ignore
        return re.compile(pattern)


external_base_classes = [NumpyDType(), PandasDType()]
# _pandas_dtype_classes = [
#     pd.StringDtype,
#     pd.CategoricalDtype,
#     pd.BooleanDtype,
#     pd.DatetimeTZDtype,
#     pd.Int8Dtype,
#     pd.Int16Dtype,
#     pd.Int32Dtype,
#     pd.Int64Dtype,
#     pd.UInt8Dtype,
#     pd.UInt16Dtype,
#     pd.UInt32Dtype,
#     pd.UInt64Dtype,
# ]
# pandas_dtypes = [PandasDType(pandas_dtype) for pandas_dtype in _pandas_dtype_classes]


_whitelisted_types = {
    bool,
    int,
    float,
    str,
    object,
    complex,
    list,
    set,
    tuple,
    dict,
    range,
    type,
    slice,
    np.float64,
    np.float32,
    np.uint8,
    np.uint16,
    np.uint32,
    np.uint64,
    np.int8,
    np.int16,
    np.int32,
    np.int64,
    AssertionError,
    AttributeError,
    IndexError,
    OutOfBoundsDatetime,
    ParserError,
    ValueError,
    TypeError,
    ZeroDivisionError,
}


@dataclass
class TypeSerde(ExternalTypeSerializer):
    class_: type = type

    def __init__(self, other_types: Optional[Set[Type]] = None):
        if other_types is None:
            self._whitelisted_types = _whitelisted_types
        else:
            self._whitelisted_types = _whitelisted_types | other_types

    @staticmethod
    def _fullname(type_: type) -> str:
        return f"{type_.__module__}.{type_.__qualname__}"

    def to_json(self, value: type) -> dict:
        return {"value": self._fullname(value)}

    def from_json(self, value: str) -> type:  # type: ignore
        return {self._fullname(class_): class_ for class_ in self._whitelisted_types}[value]


scalar_types: List[ExternalTypeSerializer] = [
    DateSerde(),
    DateTimeSerde(),
    TimeStampSerde(),
    PeriodSerde(),
    IntervalSerde(),
    TimeSerde(),
    # NumpyDType(),
    NumpyF32Serde(),
    NumpyDateTime64Serde(),
    NumpyBusDayCalendarSerde(),
    NumpyArray(),
    PandasNASerde(),
    PandasNaTSerde(),
    TimedeltaSerde(),
    PyTimedeltaSerde(),
    PandasCategoricalSerde(),
    PandasIntervalSerde(),
    RegexSerde(),
]
scalar_types += numpy_scalars

tseries_offset_types: List[ExternalTypeSerializer] = [
    OffsetsGenericSerde(Second, ["n"]),
    OffsetsGenericSerde(Minute, ["n"]),
    OffsetsGenericSerde(BusinessHour, ["n", "normalize", "start", "end"]),
    OffsetsGenericSerde(Hour, ["n"]),
    OffsetsGenericSerde(BusinessDay, ["n"]),
    OffsetsGenericSerde(CustomBusinessDay, ["n", "normalize", "calendar", "offset"]),
    OffsetsGenericSerde(Day, ["n"]),
    OffsetsGenericSerde(Week, ["n", "weekday"]),
    OffsetsGenericSerde(SemiMonthBegin, ["n", "day_of_month", "normalize"]),
    OffsetsGenericSerde(SemiMonthEnd, ["n", "day_of_month", "normalize"]),
    OffsetsGenericSerde(MonthBegin, ["n"]),
    OffsetsGenericSerde(MonthEnd, ["n"]),
    OffsetsGenericSerde(BMonthEnd, ["n"]),
    OffsetsGenericSerde(BMonthBegin, ["n"]),
    OffsetsGenericSerde(WeekOfMonth, ["n", "week", "weekday"]),
    OffsetsGenericSerde(LastWeekOfMonth, ["n", "weekday"]),
    OffsetsGenericSerde(BQuarterBegin, ["n", "startingMonth"]),
    OffsetsGenericSerde(BQuarterEnd, ["n", "startingMonth"]),
    OffsetsGenericSerde(QuarterBegin, ["n", "startingMonth"]),
    OffsetsGenericSerde(QuarterEnd, ["n", "startingMonth"]),
    OffsetsGenericSerde(BYearBegin, ["n", "month"]),
    OffsetsGenericSerde(BYearEnd, ["n", "month"]),
    OffsetsGenericSerde(YearBegin, ["n", "month"]),
    OffsetsGenericSerde(YearEnd, ["n", "month"]),
    OffsetsGenericSerde(FY5253, ["n", "weekday", "startingMonth", "variation"]),
    OffsetsGenericSerde(Easter, ["n"]),
    OffsetsGenericSerde(Milli, ["n"]),
    OffsetsGenericSerde(Micro, ["n"]),
    OffsetsGenericSerde(Nano, ["n"]),
]
scalar_types += tseries_offset_types

_other_types = [
    DictSerde(),
    SetSerde(),
    PyarrowDataType(),
    TupleSerde(),
    SliceSerde(),
    RangeSerde(),
    PathSerde(),
    BytesSerde(),
]

all_external_types = scalar_types + _other_types
