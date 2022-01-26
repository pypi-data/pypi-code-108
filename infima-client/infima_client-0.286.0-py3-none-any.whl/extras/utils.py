import datetime
import math
import sys
import time
from functools import partial, wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union, cast

if sys.version_info >= (3, 8):
    from typing import Protocol
else:  # for Python<3.8
    from typing_extensions import Protocol

import pandas as pd
import stringcase
import tqdm
from more_itertools import chunked

from infima_client.core.models import CoreDate, CoreFactorDate, CoreFactorDateRange
from infima_client.core.types import UNSET

# DateT = TypeVar("DateT", str, datetime.date, pd.Timestamp)
DateT = Union[str, datetime.date, pd.Timestamp]


KNOWN_DATE_COLUMNS = ["asOf", "factorDate", "issueDate", "maturityDate"]


def handle_date(dt: DateT) -> CoreDate:
    """Convert date object to CoreDate."""
    _dt = pd.Timestamp(dt).date()
    return CoreDate(year=_dt.year, month=_dt.month, day=_dt.day)


def handle_factor_date(dt: DateT) -> CoreFactorDate:
    """Convert factor date object to CoreFactorDate."""
    _dt = pd.Timestamp(dt).date()
    if _dt.day != 1:
        raise ValueError("Factor dates are expected to have day=1")
    return CoreFactorDate(year=_dt.year, month=_dt.month)


def handle_factor_date_range(
    start: Optional[DateT], end: Optional[DateT]
) -> Optional[CoreFactorDateRange]:
    """Convert start and end factor date objects to CoreFactorDateRange."""
    if start is None and end is None:
        return None
    else:
        return CoreFactorDateRange(
            start=handle_factor_date(start) if start is not None else UNSET,
            end=handle_factor_date(end) if end is not None else UNSET,
        )


def maybe_parse_known_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in KNOWN_DATE_COLUMNS:
        df = maybe_parse_date_column(df, stringcase.snakecase(col))
        df = maybe_parse_date_column(df, col)
    return df


def maybe_parse_date_column(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if col in df.columns:
        return _parse_nested_date(df, col)
    elif all([f"{col}.{attr}" in df.columns for attr in ["year", "month"]]):
        return _parse_exploded_date(df, col)
    return df


def _parse_nested_date(df: pd.DataFrame, col: str) -> pd.DataFrame:
    dt = df.pop(col)
    exploded = pd.json_normalize(dt)
    if "day" not in exploded.columns:
        exploded["day"] = 1
    df[stringcase.snakecase(col)] = pd.to_datetime(exploded).to_numpy()
    return df


def _parse_exploded_date(df: pd.DataFrame, col: str) -> pd.DataFrame:
    to_drop = []
    dt_args = {}
    for attr in ["year", "month"]:
        c = f"{col}.{attr}"
        to_drop.append(c)
        dt_args[attr] = df[c]

    c = f"{col}.day"
    if f"{col}.day" in df.columns:
        to_drop.append(c)
        dt_args["day"] = df[c]
    else:
        dt_args["day"] = 1

    df[stringcase.snakecase(col)] = pd.to_datetime(dt_args).to_numpy()
    return df.drop(to_drop, axis=1)


def maybe_explode_columns(
    df: pd.DataFrame, cols: Optional[List[str]] = None
) -> pd.DataFrame:
    if cols is None:
        return df

    for col in cols:
        if col not in df.columns:
            continue
        exploded = pd.json_normalize(df[col]).rename(columns=stringcase.snakecase)
        df.drop(col, axis=1, inplace=True)
        df = pd.concat([df, exploded], axis=1)

    return df


def maybe_get_column(df: pd.DataFrame, col: Optional[str] = None) -> pd.DataFrame:
    if col is None or col not in df.columns:
        return df
    return df[[col]]


def maybe_wide(df: pd.DataFrame, on: Optional[str] = None) -> pd.DataFrame:
    if on is None or on not in df.index.names:
        return df
    return df.unstack(on)


class Response(Protocol):
    """Mock class for helping type mapped attributes in Model objects."""

    additional_properties: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        pass

    @property
    def additional_keys(self) -> List[str]:
        pass

    def __getitem__(self, key: str) -> Any:
        pass

    def __setitem__(self, key: str, value: Any) -> None:
        pass

    def __delitem__(self, key: str) -> None:
        pass

    def __contains__(self, key: str) -> bool:
        pass


def response_to_frame(
    response: Response,
    path: str,
    index_cols: List[str],
    explode: Optional[List[str]] = None,
    col: Optional[str] = "cpr",
    wide_on: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    out = nested_dict_to_frame(response.to_dict(), path=path, set_index=False)
    if out is None:
        return out
    out = (
        out.pipe(maybe_explode_columns, cols=explode)
        .set_index(index_cols)
        .pipe(maybe_get_column, col=col)
        .pipe(maybe_wide, on=wide_on)
    )
    return out


def nested_dict_to_frame(
    data: Dict[str, Dict[str, Any]],
    path: str,
    set_index: bool = True,
) -> Optional[pd.DataFrame]:
    def _recurse(
        data: Union[Dict[str, Dict[str, Any]], Dict[str, List[Any]]],
        keys: List[Tuple[str, List[str]]],
        meta: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        records = []
        key, extra_meta_keys = keys[0]
        keys_remain = keys[1:]
        is_final = len(keys_remain) == 0  # on last level
        is_wild = "(*)" in key  # is a wildcard key
        key = key.replace("(*)", "")

        if is_wild:
            for k in extra_meta_keys:
                meta[k] = data[k]
            data_dict = cast(Dict[str, Dict[str, Any]], data)
            # wildcard keys mean the dict keys should become values in an index level
            for idx, val in data_dict.items():
                meta[key] = idx  # update the meta data with the key value
                if is_final:
                    # objs from the last level should be records
                    val.update(meta)
                    records.append(val)
                else:
                    # keep recursing but with updated meta
                    records.extend(_recurse(val, keys_remain, meta))
        elif is_final and isinstance(data[key], list):
            for k in extra_meta_keys:
                meta[k] = data[k]
            recs = cast(List[Any], data[key])
            for rec in recs:
                rec.update(meta)
                records.append(rec)
        else:
            for k in extra_meta_keys:
                meta[k] = data[k]
            # regular keys should be recursed into
            data_ = cast(Dict[str, Dict[str, Any]], data[key])
            records.extend(_recurse(data_, keys_remain, meta))

        return records

    def _parse_path(path: str) -> List[Tuple[str, List[str]]]:
        out = []
        tokens = path.split("->")
        for token in tokens:
            keys = token.split(",")
            primary = keys[-1]
            meta = keys[:-1]
            out.append((primary, meta))
        return out

    keys = _parse_path(path)
    recs = _recurse(data, keys, {})

    index_levels = [k[0].replace("(*)", "") for k in keys if "(*)" in k[0]]

    if recs:
        df = (
            pd.DataFrame.from_records(recs)
            .pipe(maybe_parse_known_date_columns)
            .rename(columns=stringcase.snakecase)
        )
        if set_index:
            df = df.set_index(index_levels)
        return df
    else:
        return None


def simple_dict_to_frame(
    data: Dict[str, Any],
    index_name: str,
) -> Optional[pd.DataFrame]:
    if not data:
        return None
    df = (
        pd.DataFrame.from_dict(data, orient="index")
        .pipe(maybe_parse_known_date_columns)
        .rename(columns=stringcase.snakecase)
    )
    df.index = df.index.rename(index_name)
    return df


DEFAULT_CHUNK_SIZE = 1_000

T = TypeVar("T")
FChunker = Callable[..., Optional[T]]


class Catter(Protocol):
    def __call__(self, vals: List[T]) -> Optional[T]:
        ...


def chunker(
    col: str, catter: Catter, chunk_size: int = DEFAULT_CHUNK_SIZE
) -> Callable[[FChunker[T]], FChunker[T]]:
    def _deco(func: FChunker[Optional[T]]) -> FChunker[Optional[T]]:
        @wraps(func)
        def _chunked_func(*args: Any, **kwargs: Any) -> Optional[T]:
            size = kwargs.pop("chunk_size", chunk_size) or chunk_size
            items = kwargs.pop(col)
            it = chunked(items, size)

            progress: bool = kwargs.pop("progress", False)
            if progress and len(items) > size:
                it = tqdm.tqdm(it, total=math.ceil(len(items) / size))

            coll: List[T] = []
            for chunk in it:
                kwargs[col] = chunk
                result = func(*args, **kwargs)
                if result is not None:
                    coll.append(result)

            if coll:
                return catter(coll)
            else:
                return None

        return _chunked_func

    return _deco


frame_catter = cast(Catter, partial(pd.concat, ignore_index=False, axis=0))

frame_chunker = cast(
    Callable[
        ...,
        Callable[[FChunker[Optional[pd.DataFrame]]], FChunker[Optional[pd.DataFrame]]],
    ],
    partial(chunker, catter=frame_catter),
)
