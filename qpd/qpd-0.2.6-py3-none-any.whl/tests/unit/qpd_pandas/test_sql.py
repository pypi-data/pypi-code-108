from typing import Any

import pandas as pd
from qpd.dataframe import Column, DataFrame
from qpd_pandas import QPDPandasEngine
from qpd_pandas import run_sql_on_pandas
from qpd_test.sql_suite import SQLTests
from qpd_test.utils import assert_df_eq


def test_entrypoint():
    pdf = pd.DataFrame([[0, 1], [1, 2], [0, 4]], columns=["a", "b"])
    df1 = run_sql_on_pandas(
        "SELECT a, SUM(b) AS b, COUNT(*) AS c FROM df GROUP BY a", {"df": pdf}
    )
    df2 = run_sql_on_pandas("select a+1 as a, b from df", {"df": pdf}, ignore_case=True)
    res = run_sql_on_pandas(
        """
        SELECT a.a, a.b, c, b.b AS d 
        FROM a INNER JOIN b ON a.a=b.a
        """,
        dict(a=df1, b=df2),
    )
    assert_df_eq(res, [[1, 2, 1, 1], [1, 2, 1, 4]], list("abcd"))


class SQLTests(SQLTests.Tests):
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
