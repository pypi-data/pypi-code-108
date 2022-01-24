from typing import Any

import dask.dataframe as pd
import pandas

from qpd.dataframe import Column, DataFrame
from qpd_dask import QPDDaskEngine
from qpd_test.engine_suite import QPDEngineTests
from qpd_test import assert_df_eq
from qpd.specs import AggFunctionSpec


class EngineTests(QPDEngineTests.Tests):
    def test_sort(self):
        return

    def test_agg_first_last(self):
        def assert_eq(df, gp_keys, gp_map, expected, expected_cols):
            res = self.to_pandas_df(self.op.group_agg(df, gp_keys, gp_map))
            assert_df_eq(res, expected, expected_cols)

        pdf = self.to_df([[0, 1], [0, 1], [1, None], [1, 5]], ["a", "b"])
        assert_eq(
            pdf,
            ["a"],
            {
                "b1": ("b", AggFunctionSpec("first", unique=False, dropna=False)),
                "b2": ("b", AggFunctionSpec("first", unique=False, dropna=True)),
                "b3": ("b", AggFunctionSpec("last", unique=False, dropna=False)),
                "b4": ("b", AggFunctionSpec("last", unique=False, dropna=True)),
            },
            [[1, 1, 1, 1], [5, 5, 5, 5]],
            ["b1", "b2", "b3", "b4"],
        )

    def test_window_row_number(self):
        return

    def test_window_ranks(self):
        return

    def test_window_lead_lag(self):
        return

    def test_window_sum(self):
        return

    def to_pandas_df(self, df: DataFrame) -> pandas.DataFrame:
        if isinstance(df, DataFrame):
            return self.op.to_native(df).compute()
        elif isinstance(df, pd.DataFrame):
            return df.compute()
        elif isinstance(df, pandas.DataFrame):
            return df
        else:
            raise ValueError(df)

    def to_pandas_series(self, col: Column) -> pandas.Series:
        return pandas.Series(col.native.to_dask_array().compute(), name=col.name)

    def make_qpd_engine(self):
        return QPDDaskEngine()

    def to_native_df(self, data: Any, columns: Any) -> Any:
        if isinstance(data, pd.DataFrame):
            return data
        if isinstance(data, pandas.DataFrame):
            return pd.from_pandas(data, npartitions=2)
        pdf = pandas.DataFrame(data, columns=columns)
        return pd.from_pandas(pdf, npartitions=2)
