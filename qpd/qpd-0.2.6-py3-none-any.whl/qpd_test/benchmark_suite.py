from qpd_test.tests_base import TestsBase
from typing import Any, Tuple, Iterable
from pandasql import sqldf
from timeit import timeit


class BenchmarkTests(object):
    class Tests(TestsBase):
        def _test_select(
            self, *sizes: int, repeat: int = 1
        ) -> Iterable[Tuple[int, float, float]]:
            for n in sizes:
                a = self.make_rand_df(
                    n,
                    a=int,
                    b=str,
                    c=float,
                    d=int,
                    e=bool,
                    f=str,
                    g=str,
                    h=float,
                    i=str,
                    j=int,
                    k=bool,
                    l=float,
                )
                q, s = self._time_vs_sqlite(
                    repeat,
                    """
                    SELECT l AS ll,k AS kk,j AS jj,h AS hh,f,e,b,(a+l)*(a-l) AS a FROM a
                    """,
                    a=a,
                )
                yield n, q, s

        def _test_select_where(
            self, *sizes: int, repeat: int = 1
        ) -> Iterable[Tuple[int, float, float]]:
            for n in sizes:
                a = self.make_rand_df(
                    n,
                    a=int,
                    b=str,
                    c=float,
                    d=int,
                    e=bool,
                    f=str,
                    g=str,
                    h=float,
                    i=str,
                    j=int,
                    k=bool,
                    l=float,
                )
                q, s = self._time_vs_sqlite(
                    repeat,
                    """
                    SELECT l AS ll,k AS kk,j AS jj,h AS hh,f,e,b,(a+l)*(a-l) AS a FROM a
                    WHERE l<10 OR e OR (c<0.5 AND h>0.5)
                    """,
                    a=a,
                )
                yield n, q, s

        def _test_integration_1(
            self, *sizes: int, repeat: int = 1
        ) -> Iterable[Tuple[int, float, float]]:
            for n in sizes:
                a = self.make_rand_df(
                    n, a=int, b=str, c=float, d=int, e=bool, f=str, g=str, h=float
                )
                q, s = self._time_vs_sqlite(
                    repeat,
                    """
                    WITH
                        a1 AS (
                            SELECT a+1 AS a, b, c FROM a
                        ),
                        a2 AS (
                            SELECT a,MAX(b) AS b_max, AVG(c) AS c_avg FROM a GROUP BY a
                        ),
                        a3 AS (
                            SELECT d+2 AS d, f, g, h FROM a WHERE e
                        )
                    SELECT a1.a,b,c,b_max,c_avg,f,g,h FROM a1
                        INNER JOIN a2 ON a1.a=a2.a
                        LEFT JOIN a3 ON a1.a=a3.d
                    """,
                    a=a,
                )
                yield n, q, s

        def _time_vs_sqlite(self, n: int, sql: str, **dfs: Any) -> Tuple[float, float]:
            data: Any = self.to_dfs(dfs)
            qpd_time = timeit(lambda: self._run(sql, data), number=n) / n
            data = self.to_pd_dfs(dfs)
            sqlite_time = timeit(lambda: sqldf(sql, data), number=n) / n
            return qpd_time, sqlite_time
