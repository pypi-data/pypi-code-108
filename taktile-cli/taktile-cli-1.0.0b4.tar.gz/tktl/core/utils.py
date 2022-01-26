import abc
import functools
import itertools
import time
from typing import Generator, Generic, List, Sequence, TypeVar

import pandas  # type: ignore
import pyarrow  # type: ignore
import pyarrow.parquet as pq  # type: ignore
from cached_property import cached_property  # type: ignore

from tktl.core.config import settings


def concatenate_urls(fst_part, snd_part):
    fst_part = fst_part if not fst_part.endswith("/") else fst_part[:-1]
    template = "{}{}" if snd_part.startswith("/") else "{}/{}"
    concatenated = template.format(fst_part, snd_part)
    return concatenated


def lru_cache(timeout: int, maxsize: int = 128, typed: bool = False):
    def wrapper_cache(func):
        func = functools.lru_cache(maxsize=maxsize, typed=typed)(func)
        func.delta = timeout * 10 ** 9
        func.expiration = time.monotonic_ns() + func.delta

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            if time.monotonic_ns() >= func.expiration:
                func.cache_clear()
                func.expiration = time.monotonic_ns() + func.delta
            return func(*args, **kwargs)

        wrapped_func.cache_info = func.cache_info
        wrapped_func.cache_clear = func.cache_clear
        return wrapped_func

    return wrapper_cache


def flatten(x: Sequence) -> List:
    return list(itertools.chain.from_iterable(x))


LOADED_TYPE = TypeVar("LOADED_TYPE")


class DelayedLoader(Generic[LOADED_TYPE], metaclass=abc.ABCMeta):
    def __init__(self, path: str, columns: List[str]):
        number_of_columns = len(pq.read_table(path, memory_map=True).column_names)
        self._columns = columns
        self._path = path
        self._batch_size = settings.PARQUET_BATCH_DEFAULT_ROWS_READ // number_of_columns

    def load(self, first_batch: bool = False) -> LOADED_TYPE:
        if not first_batch:
            return self._load_full()
        else:
            return self._load_first_batch()

    def to_pandas_batches(self,) -> Generator[LOADED_TYPE, None, None]:
        return (self._post_process(x.to_pandas()) for x in self.to_batches())

    def to_batches(self) -> Generator[pyarrow.RecordBatch, None, None]:
        return pq.ParquetFile(self._path, memory_map=True).iter_batches(
            batch_size=self._batch_size, columns=self._columns
        )

    def _load_full(self) -> LOADED_TYPE:
        return self._post_process(
            pq.read_table(
                self._path, columns=self._columns, memory_map=True
            ).to_pandas()
        )

    def _load_first_batch(self) -> pandas.DataFrame:
        return next(self.to_pandas_batches())

    def _post_process(self, df: pandas.DataFrame) -> LOADED_TYPE:
        pass

    @cached_property
    def schema(self):
        return next(self.to_batches()).schema


class DelayedLoaderX(DelayedLoader[pandas.DataFrame]):
    def __init__(self, path: str, label: str, columns: List[str] = None):

        if not columns:
            columns = [
                c
                for c in pq.read_table(path, memory_map=True).column_names
                if not c.startswith("__index_level_") and c != label
            ]

        super().__init__(path=path, columns=columns)

    def _post_process(self, df: pandas.DataFrame) -> pandas.DataFrame:
        return df


class DelayedLoaderXProfile(DelayedLoaderX):
    def _post_process(self, df: pandas.DataFrame) -> pandas.DataFrame:
        df.columns = [str(c) for c in df.columns]
        return df


class DelayedLoaderY(DelayedLoader[pandas.Series]):
    def __init__(self, path: str, label: str):
        self._label = label
        super().__init__(path=path, columns=[label])

    def _post_process(self, df: pandas.DataFrame) -> pandas.Series:
        return df[self._label]


def check_and_get_value(value, first_batch=False):
    if isinstance(value, DelayedLoader):
        return value.load(first_batch=first_batch)
    else:
        return value
