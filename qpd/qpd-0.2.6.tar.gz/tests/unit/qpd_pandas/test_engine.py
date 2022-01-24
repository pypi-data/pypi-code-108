from typing import Any

import pandas as pd

from qpd.dataframe import Column, DataFrame
from qpd_pandas import QPDPandasEngine
from qpd_pandas.engine import _RowsIndexer
from qpd_test.engine_suite import QPDEngineTests


class EngineTests(QPDEngineTests.Tests):
    def to_pandas_df(self, df: Any) -> pd.DataFrame:
        if isinstance(df, DataFrame):
            return self.op.to_native(df)
        elif isinstance(df, pd.DataFrame):
            return df
        else:
            raise ValueError(df)

    def to_pandas_series(self, col: Column) -> pd.Series:
        return col.native

    def make_qpd_engine(self):
        return QPDPandasEngine()

    def to_native_df(self, data: Any, columns: Any) -> Any:  # pragma: no cover
        if isinstance(data, pd.DataFrame):
            return data
        return pd.DataFrame(data, columns=columns)


def test_rows_indexer():
    r = _RowsIndexer(None, None)
    a, b = r.get_window_bounds(0)
    assert [] == a.tolist()
    assert [] == b.tolist()
    a, b = r.get_window_bounds(2)
    assert [0, 0] == a.tolist()
    assert [2, 2] == b.tolist()

    r = _RowsIndexer(None, -2)
    a, b = r.get_window_bounds(0)
    assert [] == a.tolist()
    assert [] == b.tolist()
    a, b = r.get_window_bounds(3)
    assert [0, 0, 0] == a.tolist()
    assert [0, 0, 1] == b.tolist()

    r = _RowsIndexer(None, 0)
    a, b = r.get_window_bounds(0)
    assert [] == a.tolist()
    assert [] == b.tolist()
    a, b = r.get_window_bounds(3)
    assert [0, 0, 0] == a.tolist()
    assert [1, 2, 3] == b.tolist()

    r = _RowsIndexer(None, 1)
    a, b = r.get_window_bounds(0)
    assert [] == a.tolist()
    assert [] == b.tolist()
    a, b = r.get_window_bounds(3)
    assert [0, 0, 0] == a.tolist()
    assert [2, 3, 3] == b.tolist()

    r = _RowsIndexer(-1, None)
    a, b = r.get_window_bounds(0)
    assert [] == a.tolist()
    assert [] == b.tolist()
    a, b = r.get_window_bounds(3)
    assert [0, 0, 1] == a.tolist()
    assert [3, 3, 3] == b.tolist()

    r = _RowsIndexer(0, None)
    a, b = r.get_window_bounds(0)
    assert [] == a.tolist()
    assert [] == b.tolist()
    a, b = r.get_window_bounds(3)
    assert [0, 1, 2] == a.tolist()
    assert [3, 3, 3] == b.tolist()

    r = _RowsIndexer(2, None)
    a, b = r.get_window_bounds(0)
    assert [] == a.tolist()
    assert [] == b.tolist()
    a, b = r.get_window_bounds(3)
    assert [2, 3, 3] == a.tolist()
    assert [3, 3, 3] == b.tolist()

    r = _RowsIndexer(-3, -1)
    a, b = r.get_window_bounds(0)
    assert [] == a.tolist()
    assert [] == b.tolist()
    a, b = r.get_window_bounds(3)
    assert [0, 0, 0] == a.tolist()
    assert [0, 1, 2] == b.tolist()

    r = _RowsIndexer(-1, 0)
    a, b = r.get_window_bounds(0)
    assert [] == a.tolist()
    assert [] == b.tolist()
    a, b = r.get_window_bounds(3)
    assert [0, 0, 1] == a.tolist()
    assert [1, 2, 3] == b.tolist()

    r = _RowsIndexer(0, 1)
    a, b = r.get_window_bounds(0)
    assert [] == a.tolist()
    assert [] == b.tolist()
    a, b = r.get_window_bounds(3)
    assert [0, 1, 2] == a.tolist()
    assert [2, 3, 3] == b.tolist()

    r = _RowsIndexer(2, 3)
    a, b = r.get_window_bounds(0)
    assert [] == a.tolist()
    assert [] == b.tolist()
    a, b = r.get_window_bounds(3)
    assert [2, 3, 3] == a.tolist()
    assert [3, 3, 3] == b.tolist()
