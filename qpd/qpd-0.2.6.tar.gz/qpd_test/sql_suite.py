from qpd_test.tests_base import TestsBase
import pandas as pd


class SQLTests(object):
    class Tests(TestsBase):
        def test_basic_select_from(self):
            df = self.make_rand_df(5, a=(int, 2), b=(str, 3), c=(float, 4))
            self.eq_sqlite("SELECT 1 AS a, 1.5 AS b, 'x' AS c")
            self.eq_sqlite("SELECT 1+2 AS a, 1.5*3 AS b, 'x' AS c")
            self.eq_sqlite("SELECT * FROM a", a=df)
            self.eq_sqlite("SELECT * FROM a AS x", a=df)
            self.eq_sqlite("SELECT b AS bb, a+1-2*3.0/4 AS cc, x.* FROM a AS x", a=df)
            self.eq_sqlite("SELECT *, 1 AS x, 2.5 AS y, 'z' AS z FROM a AS x", a=df)
            self.eq_sqlite("SELECT *, -(1.0+a)/3 AS x, +(2.5) AS y FROM a AS x", a=df)

        def test_case_when(self):
            a = self.make_rand_df(100, a=(int, 20), b=(str, 30), c=(float, 40))
            self.eq_sqlite(
                """
                SELECT a,b,c,
                    CASE
                        WHEN a<10 THEN a+3
                        WHEN c<0.5 THEN a+5
                        ELSE (1+2)*3 + a
                    END AS d
                FROM a
                """,
                a=a,
            )

        def test_drop_duplicates(self):
            # simplest
            a = self.make_rand_df(100, a=int, b=int)
            self.eq_sqlite(
                """
                SELECT DISTINCT b, a FROM a
                """,
                a=a,
            )
            # mix of number and nan
            a = self.make_rand_df(100, a=(int, 50), b=(int, 50))
            self.eq_sqlite(
                """
                SELECT DISTINCT b, a FROM a
                """,
                a=a,
            )
            # mix of number and string and nulls
            a = self.make_rand_df(100, a=(int, 50), b=(str, 50), c=float)
            self.eq_sqlite(
                """
                SELECT DISTINCT b, a FROM a
                """,
                a=a,
            )

        def test_order_by_no_limit(self):
            a = self.make_rand_df(100, a=(int, 50), b=(str, 50), c=float)
            self.eq_sqlite(
                """
                SELECT DISTINCT b, a FROM a ORDER BY a
                """,
                a=a,
            )

        def test_order_by_limit(self):
            a = self.make_rand_df(100, a=(int, 50), b=(str, 50), c=float)
            self.eq_sqlite(
                """
                SELECT DISTINCT b, a FROM a LIMIT 0
                """,
                a=a,
            )
            self.eq_sqlite(
                """
                SELECT DISTINCT b, a FROM a ORDER BY a LIMIT 2
                """,
                a=a,
            )
            self.eq_sqlite(
                """
                SELECT b, a FROM a
                    ORDER BY a NULLS LAST, b NULLS FIRST LIMIT 10
                """,
                a=a,
            )

        def test_where(self):
            df = self.make_rand_df(100, a=(int, 30), b=(str, 30), c=(float, 30))
            self.eq_sqlite("SELECT * FROM a WHERE TRUE OR TRUE", a=df)
            self.eq_sqlite("SELECT * FROM a WHERE TRUE AND TRUE", a=df)
            self.eq_sqlite("SELECT * FROM a WHERE FALSE OR FALSE", a=df)
            self.eq_sqlite("SELECT * FROM a WHERE FALSE AND FALSE", a=df)

            self.eq_sqlite("SELECT * FROM a WHERE TRUE OR b<='ssssss8'", a=df)
            self.eq_sqlite("SELECT * FROM a WHERE TRUE AND b<='ssssss8'", a=df)
            self.eq_sqlite("SELECT * FROM a WHERE FALSE OR b<='ssssss8'", a=df)
            self.eq_sqlite("SELECT * FROM a WHERE FALSE AND b<='ssssss8'", a=df)
            self.eq_sqlite("SELECT * FROM a WHERE a==10 OR b<='ssssss8'", a=df)
            self.eq_sqlite(
                "SELECT * FROM a WHERE c IS NOT NULL OR (a<5 AND b IS NOT NULL)", a=df
            )

            df = self.make_rand_df(100, a=(float, 30), b=(float, 30), c=(float, 30))
            self.eq_sqlite("SELECT * FROM a WHERE a<0.5 AND b<0.5 AND c<0.5", a=df)
            self.eq_sqlite("SELECT * FROM a WHERE a<0.5 OR b<0.5 AND c<0.5", a=df)
            self.eq_sqlite("SELECT * FROM a WHERE a IS NULL OR (b<0.5 AND c<0.5)", a=df)
            self.eq_sqlite(
                "SELECT * FROM a WHERE a*b IS NULL OR (b*c<0.5 AND c*a<0.5)", a=df
            )

        def test_in_between(self):
            df = self.make_rand_df(10, a=(int, 3), b=(str, 3))
            self.eq_sqlite("SELECT * FROM a WHERE a IN (2,4,6)", a=df)
            self.eq_sqlite("SELECT * FROM a WHERE a BETWEEN 2 AND 4+1", a=df)
            self.eq_sqlite("SELECT * FROM a WHERE a NOT IN (2,4,6)", a=df)
            self.eq_sqlite("SELECT * FROM a WHERE a NOT BETWEEN 2 AND 4+1", a=df)

        def test_join_inner(self):
            a = self.make_rand_df(100, a=(int, 40), b=(str, 40), c=(float, 40))
            b = self.make_rand_df(80, d=(float, 10), a=(int, 10), b=(str, 10))
            self.eq_sqlite(
                "SELECT a.*, d, d*c AS x FROM a INNER JOIN b ON a.a=b.a AND a.b=b.b",
                a=a,
                b=b,
            )

        def test_join_left(self):
            a = self.make_rand_df(100, a=(int, 40), b=(str, 40), c=(float, 40))
            b = self.make_rand_df(80, d=(float, 10), a=(int, 10), b=(str, 10))
            self.eq_sqlite(
                "SELECT a.*, d, d*c AS x FROM a LEFT JOIN b ON a.a=b.a AND a.b=b.b",
                a=a,
                b=b,
            )

        def test_join_right(self):
            a = ([[0, 1], [None, 3]], ["a", "b"])
            b = ([[0, 10], [None, 30]], ["a", "c"])
            self.assert_eq(
                dict(a=a, b=b),
                "SELECT a.*,c FROM a RIGHT JOIN b ON a.a=b.a",
                [[0, 1, 10], [None, None, 30]],
                ["a", "b", "c"],
            )

        def test_join_full(self):
            a = ([[0, 1], [None, 3]], ["a", "b"])
            b = ([[0, 10], [None, 30]], ["a", "c"])
            self.assert_eq(
                dict(a=a, b=b),
                "SELECT a.*,c FROM a FULL JOIN b ON a.a=b.a",
                [[0, 1, 10], [None, 3, None], [None, None, 30]],
                ["a", "b", "c"],
            )

        def test_join_cross(self):
            a = self.make_rand_df(10, a=(int, 4), b=(str, 4), c=(float, 4))
            b = self.make_rand_df(20, dd=(float, 1), aa=(int, 1), bb=(str, 1))
            self.eq_sqlite("SELECT * FROM a CROSS JOIN b", a=a, b=b)

        def test_join_semi(self):
            a = ([[0, 1], [None, 3]], ["a", "b"])
            b = ([[0, 10], [None, 30]], ["a", "b"])
            self.assert_eq(
                dict(a=a, b=b),
                "SELECT * FROM a LEFT SEMI JOIN b ON a.a=b.a",
                [[0, 1]],
                ["a", "b"],
            )
            self.assert_eq(
                dict(a=a, b=b),
                "SELECT a.* FROM a LEFT SEMI JOIN b ON a.a=b.a",
                [[0, 1]],
                ["a", "b"],
            )

        def test_join_anti(self):
            a = ([[0, 1], [None, 3]], ["a", "b"])
            b = ([[0, 10], [None, 30]], ["a", "b"])
            self.assert_eq(
                dict(a=a, b=b),
                "SELECT * FROM a LEFT ANTI JOIN b ON a.a=b.a",
                [[None, 3]],
                ["a", "b"],
            )
            self.assert_eq(
                dict(a=a, b=b),
                "SELECT a.* FROM a LEFT ANTI JOIN b ON a.a=b.a",
                [[None, 3]],
                ["a", "b"],
            )

        def test_join_multi(self):
            a = self.make_rand_df(100, a=(int, 40), b=(str, 40), c=(float, 40))
            b = self.make_rand_df(80, d=(float, 10), a=(int, 10), b=(str, 10))
            c = self.make_rand_df(80, dd=(float, 10), a=(int, 10), b=(str, 10))
            self.eq_sqlite(
                """
                SELECT a.*,d,dd FROM a
                    INNER JOIN b ON a.a=b.a AND a.b=b.b
                    INNER JOIN c ON a.a=c.a AND c.b=b.b
                """,
                a=a,
                b=b,
                c=c,
            )

        def test_agg_count_no_group_by(self):
            a = self.make_rand_df(
                100, a=(int, 50), b=(str, 50), c=(int, 30), d=(str, 40), e=(float, 40)
            )
            self.eq_sqlite(
                """
                SELECT
                    COUNT(a) AS c_a,
                    COUNT(DISTINCT a) AS cd_a,
                    COUNT(b) AS c_b,
                    COUNT(DISTINCT b) AS cd_b,
                    COUNT(c) AS c_c,
                    COUNT(DISTINCT c) AS cd_c,
                    COUNT(d) AS c_d,
                    COUNT(DISTINCT d) AS cd_d,
                    COUNT(e) AS c_e,
                    COUNT(DISTINCT a) AS cd_e
                FROM a
                """,
                a=a,
            )
            b = ([[1, "x", 1.5], [2, None, 2.5], [2, None, 2.5]], ["a", "b", "c"])
            self.assert_eq(
                dict(a=a, b=b),
                """
                SELECT
                    COUNT(*) AS a1,
                    COUNT(DISTINCT *) AS a2,
                    COUNT(a, b) AS a3,
                    COUNT(DISTINCT a,b) AS a4,
                    COUNT(a, b) + COUNT(DISTINCT a,b) AS a5
                FROM b
                """,
                [[3, 2, 3, 2, 5]],
                ["a1", "a2", "a3", "a4", "a5"],
            )

        def test_agg_count(self):
            a = self.make_rand_df(
                100, a=(int, 50), b=(str, 50), c=(int, 30), d=(str, 40), e=(float, 40)
            )
            self.eq_sqlite(
                """
                SELECT
                    a, b, a+1 AS c,
                    COUNT(c) AS c_c,
                    COUNT(DISTINCT c) AS cd_c,
                    COUNT(d) AS c_d,
                    COUNT(DISTINCT d) AS cd_d,
                    COUNT(e) AS c_e,
                    COUNT(DISTINCT a) AS cd_e
                FROM a GROUP BY a, b
                """,
                a=a,
            )
            b = ([[1, "x", 1.5], [2, None, 2.5], [2, None, 2.5]], ["a", "b", "c"])
            self.assert_eq(
                dict(a=a, b=b),
                """
                SELECT
                    a, b,
                    COUNT(*) AS a1,
                    COUNT(DISTINCT *) AS a2,
                    COUNT(c) AS a3,
                    COUNT(DISTINCT c) AS a4,
                    COUNT(c) + COUNT(DISTINCT c) AS a5
                FROM b GROUP BY a, b
                """,
                [[1, "x", 1, 1, 1, 1, 2], [2, None, 2, 1, 2, 1, 3]],
                ["a", "b", "a1", "a2", "a3", "a4", "a5"],
            )

        def test_agg_sum_avg_no_group_by(self):
            self.eq_sqlite(
                """
                SELECT
                    SUM(a) AS sum_a,
                    AVG(a) AS avg_a
                FROM a
                """,
                a=([[float("nan")]], ["a"]),
            )
            a = self.make_rand_df(
                100, a=(int, 50), b=(str, 50), c=(int, 30), d=(str, 40), e=(float, 40)
            )
            self.eq_sqlite(
                """
                SELECT
                    SUM(a) AS sum_a,
                    AVG(a) AS avg_a,
                    SUM(c) AS sum_c,
                    AVG(c) AS avg_c,
                    SUM(e) AS sum_e,
                    AVG(e) AS avg_e,
                    SUM(a)+AVG(e) AS mix_1,
                    SUM(a+e) AS mix_2
                FROM a
                """,
                a=a,
            )

        def test_agg_sum_avg(self):
            a = self.make_rand_df(
                100, a=(int, 50), b=(str, 50), c=(int, 30), d=(str, 40), e=(float, 40)
            )
            self.eq_sqlite(
                """
                SELECT
                    a,b, a+1 AS c,
                    SUM(c) AS sum_c,
                    AVG(c) AS avg_c,
                    SUM(e) AS sum_e,
                    AVG(e) AS avg_e,
                    SUM(a)+AVG(e) AS mix_1,
                    SUM(a+e) AS mix_2
                FROM a GROUP BY a,b
                """,
                a=a,
            )

        def test_agg_min_max_no_group_by(self):
            a = self.make_rand_df(
                100, a=(int, 50), b=(str, 50), c=(int, 30), d=(str, 40), e=(float, 40)
            )
            self.eq_sqlite(
                """
                SELECT
                    MIN(a) AS min_a,
                    MAX(a) AS max_a,
                    MIN(b) AS min_b,
                    MAX(b) AS max_b,
                    MIN(c) AS min_c,
                    MAX(c) AS max_c,
                    MIN(d) AS min_d,
                    MAX(d) AS max_d,
                    MIN(e) AS min_e,
                    MAX(e) AS max_e,
                    MIN(a+e) AS mix_1,
                    MIN(a)+MIN(e) AS mix_2
                FROM a
                """,
                a=a,
            )

        def test_agg_min_max(self):
            a = self.make_rand_df(
                100, a=(int, 50), b=(str, 50), c=(int, 30), d=(str, 40), e=(float, 40)
            )
            self.eq_sqlite(
                """
                SELECT
                    a, b, a+1 AS c,
                    MIN(c) AS min_c,
                    MAX(c) AS max_c,
                    MIN(d) AS min_d,
                    MAX(d) AS max_d,
                    MIN(e) AS min_e,
                    MAX(e) AS max_e,
                    MIN(a+e) AS mix_1,
                    MIN(a)+MIN(e) AS mix_2
                FROM a GROUP BY a, b
                """,
                a=a,
            )

        def test_agg_first_last_no_group_by(self):
            a = ([[1, "x", None], [2, None, 2.5], [2, None, 2.5]], ["a", "b", "c"])
            self.assert_eq(
                dict(a=a),
                """
                SELECT
                    FIRST(a) AS a1,
                    LAST(a) AS a2,
                    FIRST_VALUE(b) AS a3,
                    LAST_VALUE(b) AS a4,
                    FIRST_VALUE(c) AS a5,
                    LAST_VALUE(c) AS a6
                FROM a
                """,
                [[1, 2, "x", None, None, 2.5]],
                ["a1", "a2", "a3", "a4", "a5", "a6"],
            )

        def test_agg_first_last(self):
            a = ([[1, "x", None], [2, None, 3.5], [2, 1, 2.5]], ["a", "b", "c"])
            self.assert_eq(
                dict(a=a),
                """
                SELECT
                    a,
                    FIRST(b) AS a1,
                    LAST(b) AS a2,
                    FIRST_VALUE(c) AS a3,
                    LAST_VALUE(c) AS a4
                FROM a GROUP BY a
                """,
                [[1, "x", "x", None, None], [2, None, 1, 3.5, 2.5]],
                ["a", "a1", "a2", "a3", "a4"],
            )

        def test_window_row_number(self):
            a = self.make_rand_df(100, a=int, b=(float, 50))
            self.eq_sqlite(
                """
                SELECT *,
                    ROW_NUMBER() OVER (ORDER BY a ASC, b DESC NULLS FIRST) AS a1,
                    ROW_NUMBER() OVER (ORDER BY a ASC, b DESC NULLS LAST) AS a2,
                    ROW_NUMBER() OVER (ORDER BY a ASC, b ASC NULLS FIRST) AS a3,
                    ROW_NUMBER() OVER (ORDER BY a ASC, b ASC NULLS LAST) AS a4,
                    ROW_NUMBER() OVER (PARTITION BY a ORDER BY a,b DESC) AS a5
                FROM a
                """,
                a=a,
            )

            a = self.make_rand_df(
                100, a=(int, 50), b=(str, 50), c=(int, 30), d=(str, 40), e=float
            )
            self.eq_sqlite(
                """
                SELECT *,
                    ROW_NUMBER() OVER (ORDER BY a ASC, b DESC NULLS FIRST, e) AS a1,
                    ROW_NUMBER() OVER (ORDER BY a ASC, b DESC NULLS LAST, e) AS a2,
                    ROW_NUMBER() OVER (PARTITION BY a ORDER BY a,b DESC, e) AS a3,
                    ROW_NUMBER() OVER (PARTITION BY a,c ORDER BY a,b DESC, e) AS a4
                FROM a
                """,
                a=a,
            )

        def test_window_row_number_partition_by(self):
            a = self.make_rand_df(100, a=int, b=(float, 50))
            self.eq_sqlite(
                """
                SELECT *,
                    ROW_NUMBER() OVER (PARTITION BY a ORDER BY a,b DESC) AS a5
                FROM a
                """,
                a=a,
            )

            a = self.make_rand_df(
                100, a=(int, 50), b=(str, 50), c=(int, 30), d=(str, 40), e=float
            )
            self.eq_sqlite(
                """
                SELECT *,
                    ROW_NUMBER() OVER (PARTITION BY a ORDER BY a,b DESC, e) AS a3,
                    ROW_NUMBER() OVER (PARTITION BY a,c ORDER BY a,b DESC, e) AS a4
                FROM a
                """,
                a=a,
            )

        def test_window_ranks(self):
            a = self.make_rand_df(100, a=int, b=(float, 50), c=(str, 50))
            self.eq_sqlite(
                """
                SELECT *,
                    RANK() OVER (PARTITION BY a ORDER BY b DESC NULLS FIRST, c) AS a1,
                    DENSE_RANK() OVER (ORDER BY a ASC, b DESC NULLS LAST, c DESC) AS a2,
                    PERCENT_RANK() OVER (ORDER BY a ASC, b ASC NULLS LAST, c) AS a4
                FROM a
                """,
                a=a,
            )

        def test_window_ranks_partition_by(self):
            a = self.make_rand_df(100, a=int, b=(float, 50), c=(str, 50))
            self.eq_sqlite(
                """
                SELECT *,
                    RANK() OVER (PARTITION BY a ORDER BY b DESC NULLS FIRST, c) AS a1,
                    DENSE_RANK() OVER
                        (PARTITION BY a ORDER BY a ASC, b DESC NULLS LAST, c DESC)
                        AS a2,
                    PERCENT_RANK() OVER
                        (PARTITION BY a ORDER BY a ASC, b ASC NULLS LAST, c) AS a4
                FROM a
                """,
                a=a,
            )

        def test_window_lead_lag(self):
            a = self.make_rand_df(100, a=float, b=(int, 50), c=(str, 50))
            self.eq_sqlite(
                """
                SELECT
                    LEAD(b,1) OVER (ORDER BY a) AS a1,
                    LEAD(b,2,10) OVER (ORDER BY a) AS a2,
                    LEAD(b,1) OVER (PARTITION BY c ORDER BY a) AS a3,
                    LEAD(b,1) OVER (PARTITION BY c ORDER BY b, a ASC NULLS LAST) AS a5,

                    LAG(b,1) OVER (ORDER BY a) AS b1,
                    LAG(b,2,10) OVER (ORDER BY a) AS b2,
                    LAG(b,1) OVER (PARTITION BY c ORDER BY a) AS b3,
                    LAG(b,1) OVER (PARTITION BY c ORDER BY b, a ASC NULLS LAST) AS b5
                FROM a
                """,
                a=a,
            )

        def test_window_lead_lag_partition_by(self):
            a = self.make_rand_df(100, a=float, b=(int, 50), c=(str, 50))
            self.eq_sqlite(
                """
                SELECT
                    LEAD(b,1,10) OVER (PARTITION BY c ORDER BY a) AS a3,
                    LEAD(b,1) OVER (PARTITION BY c ORDER BY b, a ASC NULLS LAST) AS a5,

                    LAG(b,1) OVER (PARTITION BY c ORDER BY a) AS b3,
                    LAG(b,1) OVER (PARTITION BY c ORDER BY b, a ASC NULLS LAST) AS b5
                FROM a
                """,
                a=a,
            )

        def test_window_sum_avg(self):
            a = self.make_rand_df(100, a=float, b=(int, 50), c=(str, 50))
            for func in ["SUM", "AVG"]:
                self.eq_sqlite(
                    f"""
                    SELECT a,b,
                        {func}(b) OVER () AS a1,
                        {func}(b) OVER (PARTITION BY c) AS a2,
                        {func}(b+a) OVER (PARTITION BY c,b) AS a3,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS a4,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a DESC
                            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS a5,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
                            AS a6
                    FROM a
                    """,
                    a=a,
                )
                # >= 1.1.0 has bug on these agg function with groupby+rolloing
                # https://github.com/pandas-dev/pandas/issues/35557
                if pd.__version__ < "1.1":
                    # irregular windows
                    self.eq_sqlite(
                        f"""
                        SELECT a,b,
                            {func}(b) OVER (PARTITION BY b ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 1 PRECEDING) AS a6,
                            {func}(b) OVER (PARTITION BY b ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 1 FOLLOWING) AS a7,
                            {func}(b) OVER (PARTITION BY b ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND UNBOUNDED FOLLOWING) AS a8
                        FROM a
                        """,
                        a=a,
                    )

        def test_window_sum_avg_partition_by(self):
            a = self.make_rand_df(100, a=float, b=(int, 50), c=(str, 50))
            for func in ["SUM", "AVG"]:
                self.eq_sqlite(
                    f"""
                    SELECT a,b,
                        {func}(b+a) OVER (PARTITION BY c,b) AS a3,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS a4,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a DESC
                            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS a5,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
                            AS a6
                    FROM a
                    """,
                    a=a,
                )
                # 1.1.0 has bug on these agg function with groupby+rolloing
                # https://github.com/pandas-dev/pandas/issues/35557
                if pd.__version__ < "1.1":
                    # irregular windows
                    self.eq_sqlite(
                        f"""
                        SELECT a,b,
                            {func}(b) OVER (PARTITION BY b ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 1 PRECEDING) AS a6,
                            {func}(b) OVER (PARTITION BY b ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 1 FOLLOWING) AS a7,
                            {func}(b) OVER (PARTITION BY b ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND UNBOUNDED FOLLOWING) AS a8
                        FROM a
                        """,
                        a=a,
                    )

        def test_window_min_max(self):
            for func in ["MIN", "MAX"]:
                a = self.make_rand_df(100, a=float, b=(int, 50), c=(str, 50))
                self.eq_sqlite(
                    f"""
                    SELECT a,b,
                        {func}(b) OVER () AS a1,
                        {func}(b) OVER (PARTITION BY c) AS a2,
                        {func}(b+a) OVER (PARTITION BY c,b) AS a3,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS a4,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a DESC
                            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS a5,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
                            AS a6
                    FROM a
                    """,
                    a=a,
                )
                # < 1.1.0 has bugs on these agg function with rolloing (no group by)
                if pd.__version__ >= "1.1":
                    # irregular windows
                    self.eq_sqlite(
                        f"""
                        SELECT a,b,
                            {func}(b) OVER (ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 1 PRECEDING) AS a6,
                            {func}(b) OVER (ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 1 FOLLOWING) AS a7,
                            {func}(b) OVER (ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND UNBOUNDED FOLLOWING) AS a8
                        FROM a
                        """,
                        a=a,
                    )
                # == 1.1.0 has bugs on these agg function with rolloing (with group by)
                # https://github.com/pandas-dev/pandas/issues/35557
                # < 1.1.0 has bugs on nulls when rolling with forward looking
                if pd.__version__ < "1.1":
                    b = self.make_rand_df(10, a=float, b=(int, 0), c=(str, 0))
                    self.eq_sqlite(
                        f"""
                        SELECT a,b,
                            {func}(b) OVER (PARTITION BY b ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 1 PRECEDING) AS a6
                        FROM a
                        """,
                        a=b,
                    )

        def test_window_min_max_partition_by(self):
            for func in ["MIN", "MAX"]:
                a = self.make_rand_df(100, a=float, b=(int, 50), c=(str, 50))
                self.eq_sqlite(
                    f"""
                    SELECT a,b,
                        {func}(b) OVER (PARTITION BY c) AS a2,
                        {func}(b+a) OVER (PARTITION BY c,b) AS a3,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS a4,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a DESC
                            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS a5,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
                            AS a6
                    FROM a
                    """,
                    a=a,
                )
                # >= 1.1.0 has bugs on these agg function with rolloing (with group by)
                # https://github.com/pandas-dev/pandas/issues/35557
                # < 1.1.0 has bugs on nulls when rolling with forward looking
                if pd.__version__ < "1.1":
                    b = self.make_rand_df(10, a=float, b=(int, 0), c=(str, 0))
                    self.eq_sqlite(
                        f"""
                        SELECT a,b,
                            {func}(b) OVER (PARTITION BY b ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 1 PRECEDING) AS a6
                        FROM a
                        """,
                        a=b,
                    )

        def test_window_count(self):
            for func in ["COUNT"]:
                a = self.make_rand_df(100, a=float, b=(int, 50), c=(str, 50))
                self.eq_sqlite(
                    f"""
                    SELECT a,b,
                        {func}(b) OVER () AS a1,
                        {func}(b) OVER (PARTITION BY c) AS a2,
                        {func}(b+a) OVER (PARTITION BY c,b) AS a3,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS a4,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a DESC
                            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS a5,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
                            AS a6,

                        {func}(c) OVER () AS b1,
                        {func}(c) OVER (PARTITION BY c) AS b2,
                        {func}(c) OVER (PARTITION BY c,b) AS b3,
                        {func}(c) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS b4,
                        {func}(c) OVER (PARTITION BY b ORDER BY a DESC
                            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS b5,
                        {func}(c) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
                            AS b6
                    FROM a
                    """,
                    a=a,
                )
                # < 1.1.0 has bugs on these agg function with rolloing (no group by)
                # == 1.1.0 has this bug
                # https://github.com/pandas-dev/pandas/issues/35579
                if pd.__version__ >= "1.1":
                    # irregular windows
                    self.eq_sqlite(
                        f"""
                        SELECT a,b,
                            {func}(b) OVER (ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 0 PRECEDING) AS a6,
                            {func}(b) OVER (PARTITION BY c ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 0 PRECEDING) AS a9,

                            {func}(c) OVER (ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 0 PRECEDING) AS b6,
                            {func}(c) OVER (PARTITION BY c ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 0 PRECEDING) AS b9
                        FROM a
                        """,
                        a=a,
                    )

        def test_window_count_partition_by(self):
            for func in ["COUNT"]:
                a = self.make_rand_df(100, a=float, b=(int, 50), c=(str, 50))
                self.eq_sqlite(
                    f"""
                    SELECT a,b,
                        {func}(b) OVER (PARTITION BY c) AS a2,
                        {func}(b+a) OVER (PARTITION BY c,b) AS a3,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS a4,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a DESC
                            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS a5,
                        {func}(b+a) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
                            AS a6,

                        {func}(c) OVER (PARTITION BY c) AS b2,
                        {func}(c) OVER (PARTITION BY c,b) AS b3,
                        {func}(c) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS b4,
                        {func}(c) OVER (PARTITION BY b ORDER BY a DESC
                            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS b5,
                        {func}(c) OVER (PARTITION BY b ORDER BY a
                            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
                            AS b6
                    FROM a
                    """,
                    a=a,
                )
                # < 1.1.0 has bugs on these agg function with rolloing (no group by)
                # == 1.1.0 has this bug
                # https://github.com/pandas-dev/pandas/issues/35579
                if pd.__version__ >= "1.1":
                    # irregular windows
                    self.eq_sqlite(
                        f"""
                        SELECT a,b,
                            {func}(b) OVER (PARTITION BY c ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 0 PRECEDING) AS a9,

                            {func}(c) OVER (PARTITION BY c ORDER BY a DESC
                                ROWS BETWEEN 2 PRECEDING AND 0 PRECEDING) AS b9
                        FROM a
                        """,
                        a=a,
                    )

        def test_nested_query(self):
            a = self.make_rand_df(100, a=float, b=(int, 50), c=(str, 50))
            self.eq_sqlite(
                """
                SELECT * FROM (
                SELECT *,
                    ROW_NUMBER() OVER (PARTITION BY c ORDER BY b, a ASC NULLS LAST) AS r
                FROM a)
                WHERE r=1
                """,
                a=a,
            )

        def test_union(self):
            a = self.make_rand_df(30, b=(int, 10), c=(str, 10))
            b = self.make_rand_df(80, b=(int, 50), c=(str, 50))
            c = self.make_rand_df(100, b=(int, 50), c=(str, 50))
            self.eq_sqlite(
                """
                SELECT * FROM a
                    UNION SELECT * FROM b
                    UNION SELECT * FROM c
                """,
                a=a,
                b=b,
                c=c,
            )
            self.eq_sqlite(
                """
                SELECT * FROM a
                    UNION ALL SELECT * FROM b
                    UNION ALL SELECT * FROM c
                """,
                a=a,
                b=b,
                c=c,
            )

        def test_except(self):
            a = self.make_rand_df(30, b=(int, 10), c=(str, 10))
            b = self.make_rand_df(80, b=(int, 50), c=(str, 50))
            c = self.make_rand_df(100, b=(int, 50), c=(str, 50))
            self.eq_sqlite(
                """
                SELECT * FROM c
                    EXCEPT SELECT * FROM b
                    EXCEPT SELECT * FROM c
                """,
                a=a,
                b=b,
                c=c,
            )

        def test_intersect(self):
            a = self.make_rand_df(30, b=(int, 10), c=(str, 10))
            b = self.make_rand_df(80, b=(int, 50), c=(str, 50))
            c = self.make_rand_df(100, b=(int, 50), c=(str, 50))
            self.eq_sqlite(
                """
                SELECT * FROM c
                    INTERSECT SELECT * FROM b
                    INTERSECT SELECT * FROM c
                """,
                a=a,
                b=b,
                c=c,
            )

        def test_with(self):
            a = self.make_rand_df(30, a=(int, 10), b=(str, 10))
            b = self.make_rand_df(80, ax=(int, 10), bx=(str, 10))
            # sqlite does not allow circular reference
            # but qpd allows reference overwrite
            self.eq_sqlite(
                """
                WITH
                    aa AS (
                        SELECT a AS aa, b AS bb FROM a
                    ),
                    c AS (
                        SELECT aa-1 AS aa, bb FROM aa
                    )
                SELECT * FROM c UNION SELECT * FROM b
                """,
                a=a,
                b=b,
            )

        def test_cast(self):
            pass

        def test_join_group_having(self):
            pass

        def test_integration_1(self):
            a = self.make_rand_df(
                100, a=int, b=str, c=float, d=int, e=bool, f=str, g=str, h=float
            )
            self.eq_sqlite(
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
