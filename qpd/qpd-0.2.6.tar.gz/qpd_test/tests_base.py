from typing import Any, Dict, List, Tuple
from unittest import TestCase

import numpy as np
import pandas as pd
from pandasql import sqldf
from datetime import datetime, timedelta

from qpd.dataframe import DataFrame, Column
from qpd import run_sql
from qpd.qpd_engine import QPDEngine
from qpd_test.utils import assert_df_eq


class TestsBase(TestCase):
    def make_qpd_engine(self) -> QPDEngine:  # pragma: no cover
        raise NotImplementedError

    def to_native_df(self, data: Any, columns: Any) -> Any:  # pragma: no cover
        raise NotImplementedError

    def to_pandas_df(self, df: DataFrame) -> pd.DataFrame:  # pragma: no cover
        raise NotImplementedError

    def to_pandas_series(self, col: Column) -> pd.Series:  # pragma: no cover
        raise NotImplementedError

    def to_df(self, data: Any, cols: Any) -> DataFrame:
        return self.op.to_df(self.to_native_df(data, cols))

    @classmethod
    def setUpClass(cls):
        cls._qpd_engine = cls.make_qpd_engine(cls)

    @property
    def op(self) -> QPDEngine:
        return self._qpd_engine  # type: ignore

    @classmethod
    def tearDownClass(cls):
        pass

    def eq_sqlite(self, sql: str, **dfs: Any) -> None:
        self.assert_eq(dfs, sql, None, None)

    def make_rand_df(self, size: int, **kwargs: Any) -> Tuple[Any, List[str]]:
        np.random.seed(0)
        data: Dict[str, np.ndarray] = {}
        for k, v in kwargs.items():
            if not isinstance(v, tuple):
                v = (v, 0.0)
            dt, null_ct = v[0], v[1]
            if dt is int:
                s = np.random.randint(10, size=size)
            elif dt is bool:
                s = np.where(np.random.randint(2, size=size), True, False)
            elif dt is float:
                s = np.random.rand(size)
            elif dt is str:
                r = [f"ssssss{x}" for x in range(10)]
                c = np.random.randint(10, size=size)
                s = np.array([r[x] for x in c])
            elif dt is datetime:
                rt = [datetime(2020, 1, 1) + timedelta(days=x) for x in range(10)]
                c = np.random.randint(10, size=size)
                s = np.array([rt[x] for x in c])
            else:
                raise NotImplementedError
            ps = pd.Series(s)
            if null_ct > 0:
                idx = np.random.choice(size, null_ct, replace=False).tolist()
                ps[idx] = None
            data[k] = ps
        pdf = pd.DataFrame(data)
        return pdf.values.tolist(), list(pdf.columns)

    def to_dfs(self, dfs: Dict[str, Any]) -> Dict[str, DataFrame]:
        res: Dict[str, DataFrame] = {}
        for k, v in dfs.items():
            if isinstance(v, DataFrame):
                res[k] = v
            elif isinstance(v, tuple):
                res[k] = self.to_df(v[0], v[1])
            else:
                res[k] = self.to_df(v, None)
        return res

    def to_pd_dfs(self, dfs: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        res: Dict[str, DataFrame] = {}
        for k, v in dfs.items():
            if isinstance(v, tuple):
                res[k] = pd.DataFrame(v[0], columns=v[1])
            elif isinstance(v, pd.DataFrame):
                res[k] = v
            else:
                raise NotImplementedError
        return res

    def assert_eq(
        self,
        dfs: Dict[str, Any],
        sql: str,
        expected: Any = None,
        expected_cols: Any = None,
    ) -> None:
        df = self.to_pandas_df(self._run(sql, self.to_dfs(dfs)))
        if expected is None:
            expected = sqldf(sql, self.to_pd_dfs(dfs))
        print("this", df)
        print(expected)
        assert_df_eq(df, expected, expected_cols)

    def assert_column_eq(self, col: Column, expected: Any) -> None:
        res = self.to_pandas_series(col)
        assert_df_eq(pd.DataFrame({"a": res}), pd.DataFrame({"a": expected}))

    def _run(self, raw_sql: str, dfs: Dict[str, Any]) -> Any:
        return run_sql(self.op, raw_sql, dfs)
