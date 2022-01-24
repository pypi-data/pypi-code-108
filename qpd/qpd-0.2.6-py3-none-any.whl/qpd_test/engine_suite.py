from typing import Any

import pandas as pd

from qpd.dataframe import Column, DataFrame
from qpd.specs import (
    AggFunctionSpec,
    ArgumentSpec,
    IsValueSpec,
    OrderBySpec,
    WindowFunctionSpec,
    WindowSpec,
    make_windowframe_spec,
)
from qpd_test.tests_base import TestsBase
from qpd_test.utils import assert_df_eq
from pytest import raises


class QPDEngineTests(object):
    class Tests(TestsBase):
        def to_df(self, data: Any, cols: Any) -> DataFrame:
            return self.op.to_df(self.to_native_df(data, cols))

        def to_native_df(self, data: Any, columns: Any) -> Any:  # pragma: no cover
            raise NotImplementedError

        def test_parse_join_types(self):
            assert "cross" == self.op.pl_utils.parse_join_type("CROss")
            assert "inner" == self.op.pl_utils.parse_join_type("join")
            assert "inner" == self.op.pl_utils.parse_join_type("Inner")
            assert "left_outer" == self.op.pl_utils.parse_join_type("left")
            assert "left_outer" == self.op.pl_utils.parse_join_type("left  outer")
            assert "right_outer" == self.op.pl_utils.parse_join_type("right")
            assert "right_outer" == self.op.pl_utils.parse_join_type("right_ outer")
            assert "full_outer" == self.op.pl_utils.parse_join_type("full")
            assert "full_outer" == self.op.pl_utils.parse_join_type(" outer ")
            assert "full_outer" == self.op.pl_utils.parse_join_type("full_outer")
            assert "left_anti" == self.op.pl_utils.parse_join_type("anti")
            assert "left_anti" == self.op.pl_utils.parse_join_type("left anti")
            assert "left_semi" == self.op.pl_utils.parse_join_type("semi")
            assert "left_semi" == self.op.pl_utils.parse_join_type("left semi")
            raises(
                NotImplementedError,
                lambda: self.op.pl_utils.parse_join_type("right semi"),
            )

        def test_comparison_op(self):
            def assert_eq(df, first, second, op, expected):
                if isinstance(first, str):
                    first = df[first]
                else:
                    first = Column(first)
                if isinstance(second, str):
                    second = df[second]
                else:
                    second = Column(second)
                self.assert_column_eq(
                    self.op.comparison_op(first, second, op), expected
                )

            assert self.op.comparison_op(Column(0), Column(1), "<").native
            assert not self.op.comparison_op(Column(0), Column(1), ">").native

            df = self.to_df([[1, None], [1, 0], [1, 1], [1, 2]], ["a", "b"])
            assert_eq(df, "a", 0, ">", [True, True, True, True])
            assert_eq(df, "a", "b", ">", [None, True, False, False])
            assert_eq(df, "a", "b", ">=", [None, True, True, False])
            assert_eq(df, "a", "b", "==", [None, False, True, False])
            assert_eq(df, "a", "b", "!=", [None, True, False, True])
            assert_eq(df, "a", "b", "<=", [None, False, True, True])
            assert_eq(df, "a", "b", "<", [None, False, False, True])

            assert_eq(df, 0, "a", ">", [False, False, False, False])
            assert_eq(df, "b", "a", ">", [None, False, False, True])
            assert_eq(df, "b", "a", ">=", [None, False, True, True])
            assert_eq(df, "b", "a", "==", [None, False, True, False])
            assert_eq(df, "b", "a", "!=", [None, True, False, True])
            assert_eq(df, "b", "a", "<=", [None, True, True, False])
            assert_eq(df, "b", "a", "<", [None, True, False, False])

            df = self.to_df([[1, None], [None, 1], [None, None]], ["a", "b"])
            assert_eq(df, "a", "b", ">", [None, None, None])
            assert_eq(df, "a", "b", "==", [None, None, None])
            assert_eq(df, "a", "b", "!=", [None, None, None])

            df = self.to_df([["x", "y"], ["x", None], ["x", "x"]], ["a", "b"])
            assert_eq(df, "a", "b", "<", [True, None, False])
            assert_eq(df, "a", "b", "==", [False, None, True])
            assert_eq(df, "a", "b", "!=", [True, None, False])

        def test_binary_logical_op(self):
            def assert_eq(df, first, second, op, expected):
                if isinstance(first, str):
                    first = df[first]
                else:
                    first = Column(first)
                if isinstance(second, str):
                    second = df[second]
                else:
                    second = Column(second)
                res = self.to_pandas_series(
                    self.op.binary_logical_op(first, second, op)
                ).tolist()
                res = [True if x > 0 else (False if x == 0 else None) for x in res]
                assert_df_eq(pd.DataFrame({"a": res}), pd.DataFrame({"a": expected}))

            df = self.to_df(
                [
                    [True, True],
                    [False, False],
                    [True, False],
                    [True, None],
                    [False, None],
                ],
                ["a", "b"],
            )
            assert_eq(df, "b", True, "and", [True, False, False, None, None])
            assert_eq(df, "b", False, "and", [False, False, False, False, False])
            assert_eq(df, "b", True, "or", [True, True, True, True, True])
            assert_eq(df, "b", False, "or", [True, False, False, None, None])

            assert_eq(df, "b", "a", "and", [True, False, False, None, False])
            assert_eq(df, "b", "a", "or", [True, False, True, True, None])

        def test_is_value(self):
            def assert_eq(values, expr, positive, expected):
                col = self.op.to_col(values)
                res = self.to_pandas_series(
                    self.op.is_value(col, IsValueSpec(expr, positive))
                )
                assert expected == res.tolist()

            assert_eq([1, 2, None], "null", False, [True, True, False])
            assert_eq([1, 2, None], "null", True, [False, False, True])
            assert_eq([True, False, None], "true", True, [True, False, False])
            assert_eq([True, False, None], "true", False, [False, True, True])
            assert_eq([True, False, None], "false", True, [False, True, False])
            assert_eq([True, False, None], "false", False, [True, False, True])

        def test_is_in(self):
            def assert_eq(df, col, positive, collection, expected):
                comp = [df[x] if isinstance(x, str) else x for x in collection]
                self.assert_column_eq(
                    self.op.is_in(df[col], *comp, positive=positive), expected
                )

            df = self.to_df([[0, 1, 1], [2, 3, 4]], ["a", "b", "c"])
            assert_eq(df, "c", True, [], [False, False])
            assert_eq(df, "c", True, [0, 1, 5], [True, False])
            assert_eq(df, "c", True, ["a", "b"], [True, False])
            assert_eq(df, "c", True, [0, "b"], [True, False])
            assert_eq(df, "c", False, [], [True, True])
            assert_eq(df, "c", False, [0, 1, 5], [False, True])
            assert_eq(df, "c", False, ["a", "b"], [False, True])
            assert_eq(df, "c", False, [0, "b"], [False, True])

            df = self.to_df([[0, 1, None]], ["a", "b", "c"])
            assert_eq(df, "c", True, [], [None])
            assert_eq(df, "c", True, [0, 1, 5], [None])
            assert_eq(df, "c", True, ["a", "b"], [None])
            assert_eq(df, "c", True, [0, "b"], [None])
            assert_eq(df, "c", False, [], [None])
            assert_eq(df, "c", False, [0, 1, 5], [None])
            assert_eq(df, "c", False, ["a", "b"], [None])
            assert_eq(df, "c", False, [0, "b"], [None])

        def test_is_between(self):
            def assert_eq(df, col, lower, upper, positive, expected):
                self.assert_column_eq(
                    self.op.is_between(
                        df[col], df[lower], df[upper], positive=positive
                    ),
                    expected,
                )

            df = self.to_df(
                [[0, 1, 1], [2, 3, 4], [None, 1, 1], [1, None, 1], [1, 1, None]],
                ["a", "b", "c"],
            )
            assert_eq(df, "c", "a", "b", True, [True, False, None, None, None])
            assert_eq(df, "c", "a", "b", False, [False, True, None, None, None])

        def test_case_when(self):
            def assert_eq(df, *cols, expected):
                def convert(v: Any) -> Any:
                    return df[v] if isinstance(v, str) else Column(v)

                cols = [convert(x) for x in cols]
                self.assert_column_eq(self.op.case_when(*cols), expected)

            a = self.to_df(
                [
                    [False, False, 1],
                    [False, True, 2],
                    [True, False, 3],
                    [True, True, 4],
                ],
                ["c1", "c2", "v"],
            )
            assert_eq(a, "c1", 10, "v", expected=[1, 2, 10, 10])
            assert_eq(a, "c1", 10, "c2", 11, "v", expected=[1, 11, 10, 10])
            assert_eq(a, "c1", 10, "c2", "v", 11, expected=[11, 2, 10, 10])

        def test_drop_duplicates(self):
            def assert_eq(df, expected, expected_cols):
                res = self.to_pandas_df(self.op.drop_duplicates(df))
                assert_df_eq(res, expected, expected_cols)

            a = self.to_df([["x", "a"], ["x", "a"], [None, None]], ["a", "b"])
            assert_eq(a, [["x", "a"], [None, None]], ["a", "b"])

        def test_order_by_limit(self):
            def assert_eq(df, order_by, limit, expected, expected_cols):
                res = self.to_pandas_df(
                    self.op.order_by_limit(df, OrderBySpec(*order_by), limit)
                )
                assert_df_eq(res, expected, expected_cols)

            a = self.to_df([["x", "a"], ["x", "a"], [None, None]], ["a", "b"])
            assert_eq(a, ["a"], 1, [[None, None]], ["a", "b"])
            assert_eq(a, ["a"], 2, [[None, None], ["x", "a"]], ["a", "b"])
            assert_eq(a, [("a", True, "last")], 2, [["x", "a"], ["x", "a"]], ["a", "b"])
            assert_eq(
                a, [("a", False, "first")], 2, [["x", "a"], [None, None]], ["a", "b"]
            )

        def test_union(self):
            def assert_eq(df1, df2, unique, expected, expected_cols):
                res = self.to_pandas_df(self.op.union(df1, df2, unique=unique))
                assert_df_eq(res, expected, expected_cols)

            a = self.to_df([["x", "a"], ["x", "a"], [None, None]], ["a", "b"])
            b = self.to_df([["xx", "aa"], [None, None], ["a", "x"]], ["b", "a"])
            assert_eq(
                a,
                b,
                False,
                [
                    ["x", "a"],
                    ["x", "a"],
                    [None, None],
                    ["xx", "aa"],
                    [None, None],
                    ["a", "x"],
                ],
                ["a", "b"],
            )
            assert_eq(
                a,
                b,
                True,
                [["x", "a"], ["xx", "aa"], [None, None], ["a", "x"]],
                ["a", "b"],
            )

        def test_intersect(self):
            def assert_eq(df1, df2, unique, expected, expected_cols):
                res = self.to_pandas_df(self.op.intersect(df1, df2, unique=unique))
                assert_df_eq(res, expected, expected_cols)

            a = self.to_df([["x", "a"], ["x", "a"], [None, None]], ["a", "b"])
            b = self.to_df(
                [["xx", "aa"], [None, None], [None, None], ["a", "x"]], ["b", "a"]
            )
            assert_eq(a, b, False, [[None, None]], ["a", "b"])
            assert_eq(a, b, True, [[None, None]], ["a", "b"])
            b = self.to_df([["xx", "aa"], [None, None], ["x", "a"]], ["b", "a"])
            assert_eq(a, b, False, [["x", "a"], ["x", "a"], [None, None]], ["a", "b"])
            assert_eq(a, b, True, [["x", "a"], [None, None]], ["a", "b"])

        def test_except(self):
            def assert_eq(df1, df2, unique, expected, expected_cols):
                res = self.to_pandas_df(self.op.except_df(df1, df2, unique=unique))
                assert_df_eq(res, expected, expected_cols)

            a = self.to_df([["x", "a"], ["x", "a"], [None, None]], ["a", "b"])
            b = self.to_df([["xx", "aa"], [None, None], ["a", "x"]], ["b", "a"])
            assert_eq(a, b, False, [["x", "a"], ["x", "a"]], ["a", "b"])
            assert_eq(a, b, True, [["x", "a"]], ["a", "b"])
            b = self.to_df([["xx", "aa"], [None, None], ["x", "a"]], ["b", "a"])
            assert_eq(a, b, False, [], ["a", "b"])
            assert_eq(a, b, True, [], ["a", "b"])

        def test_joins(self):
            def assert_eq(df1, df2, join_type, on, expected, expected_cols):
                res = self.to_pandas_df(
                    self.op.join(df1, df2, join_type=join_type, on=on)
                )
                assert_df_eq(res, expected, expected_cols)

            df1 = self.to_df([[0, 1], [2, 3]], ["a", "b"])
            df2 = self.to_df([[0, 10], [20, 30]], ["a", "c"])
            df3 = self.to_df([[0, 1], [None, 3]], ["a", "b"])
            df4 = self.to_df([[0, 10], [None, 30]], ["a", "c"])
            assert_eq(df1, df2, "inner", ["a"], [[0, 1, 10]], ["a", "b", "c"])
            assert_eq(df3, df4, "inner", ["a"], [[0, 1, 10]], ["a", "b", "c"])
            assert_eq(df1, df2, "left_semi", ["a"], [[0, 1]], ["a", "b"])
            assert_eq(df3, df4, "left_semi", ["a"], [[0, 1]], ["a", "b"])
            assert_eq(df1, df2, "left_anti", ["a"], [[2, 3]], ["a", "b"])
            assert_eq(df3, df4, "left_anti", ["a"], [[None, 3]], ["a", "b"])
            assert_eq(
                df1,
                df2,
                "left_outer",
                ["a"],
                [[0, 1, 10], [2, 3, None]],
                ["a", "b", "c"],
            )
            assert_eq(
                df3,
                df4,
                "left_outer",
                ["a"],
                [[0, 1, 10], [None, 3, None]],
                ["a", "b", "c"],
            )
            assert_eq(
                df1,
                df2,
                "right_outer",
                ["a"],
                [[0, 1, 10], [20, None, 30]],
                ["a", "b", "c"],
            )
            assert_eq(
                df3,
                df4,
                "right_outer",
                ["a"],
                [[0, 1, 10], [None, None, 30]],
                ["a", "b", "c"],
            )
            assert_eq(
                df1,
                df2,
                "full_outer",
                ["a"],
                [[0, 1, 10], [2, 3, None], [20, None, 30]],
                ["a", "b", "c"],
            )
            assert_eq(
                df3,
                df4,
                "full_outer",
                ["a"],
                [[0, 1, 10], [None, 3, None], [None, None, 30]],
                ["a", "b", "c"],
            )

            df1 = self.to_df([[0, 1], [None, 3]], ["a", "b"])
            df2 = self.to_df([[0, 10], [None, 30]], ["c", "d"])
            assert_eq(
                df1,
                df2,
                "cross",
                [],
                [
                    [0, 1, 0, 10],
                    [None, 3, 0, 10],
                    [0, 1, None, 30],
                    [None, 3, None, 30],
                ],
                ["a", "b", "c", "d"],
            )

        def test_sort(self):
            def ob(*order_by):
                ws = WindowSpec(
                    "",
                    partition_keys=[],
                    order_by=OrderBySpec(*order_by),
                    windowframe=make_windowframe_spec(""),
                )
                return WindowFunctionSpec("row_number", False, False, ws)

            def assert_eq(df, index, *order_by):
                ndf = self.op.to_native(df)
                e = ndf[ndf.columns]
                e["x"] = self.op.to_col(index).native
                self.w_eq(
                    df, ob(*order_by), [], "x", e.values.tolist(), list(e.columns)
                )

            df = self.to_df(
                [[0, 10, None], [1, None, 100], [None, 20, 300]], list("abc")
            )
            assert_eq(df, [1, 2, 3])
            assert_eq(df, [2, 3, 1], ("a", True))
            assert_eq(df, [2, 1, 3], ("a", False))
            assert_eq(df, [2, 3, 1], ("a", True, "first"))
            assert_eq(df, [1, 2, 3], ("a", True, "last"))
            assert_eq(df, [3, 2, 1], ("a", False, "first"))
            assert_eq(df, [2, 1, 3], ("a", False, "last"))

            df = self.to_df(
                [[0, 10, None], [0, 5, None], [0, None, 100], [None, 20, 300]],
                list("abc"),
            )
            assert_eq(df, [4, 3, 2, 1], ("a", True), ("b", True))
            assert_eq(df, [2, 3, 4, 1], ("a", True), ("b", False))
            assert_eq(df, [3, 2, 4, 1], ("a", True), ("b", True, "last"))
            assert_eq(df, [3, 4, 2, 1], ("a", True), ("b", False, "first"))
            assert_eq(df, [2, 3, 1, 4], ("a", True, "last"), ("b", False, "first"))

        def test_agg_first_last(self):
            def assert_eq(df, gp_keys, gp_map, expected, expected_cols):
                res = self.to_pandas_df(self.op.group_agg(df, gp_keys, gp_map))
                assert_df_eq(res, expected, expected_cols)

            pdf = self.to_df([[0, 1], [0, 1], [1, None], [1, 5], [0, None]], ["a", "b"])
            assert_eq(
                pdf,
                ["a"],
                {
                    "b1": ("b", AggFunctionSpec("first", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("first", unique=False, dropna=True)),
                    "b3": ("b", AggFunctionSpec("last", unique=False, dropna=False)),
                    "b4": ("b", AggFunctionSpec("last", unique=False, dropna=True)),
                },
                [[1.0, 1.0, None, 1.0], [None, 5.0, 5.0, 5.0]],
                ["b1", "b2", "b3", "b4"],
            )

        def test_agg_sum_mean(self):
            def assert_eq(df, gp_keys, gp_map, expected, expected_cols):
                res = self.to_pandas_df(self.op.group_agg(df, gp_keys, gp_map))
                assert_df_eq(res, expected, expected_cols)

            pdf = self.to_df([[0, 1], [0, 1], [0, 2], [1, 5], [0, None]], ["a", "b"])
            assert_eq(
                pdf,
                ["a"],
                {
                    "b1": ("b", AggFunctionSpec("sum", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("sum", unique=True, dropna=False)),
                    "b3": ("b", AggFunctionSpec("sum", unique=True, dropna=True)),
                    "b4": ("b", AggFunctionSpec("sum", unique=False, dropna=True)),
                },
                [[4, 3, 3, 4], [5, 5, 5, 5]],
                ["b1", "b2", "b3", "b4"],
            )
            pdf = self.to_df([[0, 1], [0, 1], [0, 4], [1, 5], [0, None]], ["a", "b"])
            assert_eq(
                pdf,
                ["a"],
                {
                    "b1": ("b", AggFunctionSpec("avg", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("avg", unique=True, dropna=False)),
                    "b3": ("b", AggFunctionSpec("mean", unique=True, dropna=True)),
                    "b4": ("b", AggFunctionSpec("mean", unique=False, dropna=True)),
                },
                [[2, 2.5, 2.5, 2], [5, 5, 5, 5]],
                ["b1", "b2", "b3", "b4"],
            )
            assert_eq(
                pdf,
                ["a"],
                {
                    "b1": ("b", AggFunctionSpec("sum", unique=True, dropna=False)),
                    "b2": ("b", AggFunctionSpec("avg", unique=True, dropna=False)),
                },
                [[5, 2.5], [5, 5]],
                ["b1", "b2"],
            )

        def test_agg_min_max(self):
            def assert_eq(df, gp_keys, gp_map, expected, expected_cols):
                res = self.to_pandas_df(self.op.group_agg(df, gp_keys, gp_map))
                assert_df_eq(res, expected, expected_cols)

            pdf = self.to_df([[0, 1], [0, 1], [0, 2], [1, None], [0, None]], ["a", "b"])
            assert_eq(
                pdf,
                ["a"],
                {
                    "b1": ("b", AggFunctionSpec("min", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("min", unique=True, dropna=False)),
                    "b3": ("b", AggFunctionSpec("min", unique=True, dropna=True)),
                    "b4": ("b", AggFunctionSpec("min", unique=False, dropna=True)),
                },
                [[1.0, 1.0, 1.0, 1.0], [None, None, None, None]],
                ["b1", "b2", "b3", "b4"],
            )
            assert_eq(
                pdf,
                ["a"],
                {
                    "b1": ("b", AggFunctionSpec("max", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("max", unique=True, dropna=False)),
                    "b3": ("b", AggFunctionSpec("max", unique=True, dropna=True)),
                    "b4": ("b", AggFunctionSpec("max", unique=False, dropna=True)),
                },
                [[2.0, 2.0, 2.0, 2.0], [None, None, None, None]],
                ["b1", "b2", "b3", "b4"],
            )

            pdf = self.to_df(
                [[0, "a"], [0, "a"], [0, "b"], [1, None], [0, None]], ["a", "b"]
            )
            assert_eq(
                pdf,
                ["a"],
                {
                    "b1": ("b", AggFunctionSpec("min", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("min", unique=True, dropna=False)),
                    "b3": ("b", AggFunctionSpec("min", unique=True, dropna=True)),
                    "b4": ("b", AggFunctionSpec("min", unique=False, dropna=True)),
                },
                [["a", "a", "a", "a"], [None, None, None, None]],
                ["b1", "b2", "b3", "b4"],
            )
            assert_eq(
                pdf,
                ["a"],
                {
                    "b1": ("b", AggFunctionSpec("max", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("max", unique=True, dropna=False)),
                    "b3": ("b", AggFunctionSpec("max", unique=True, dropna=True)),
                    "b4": ("b", AggFunctionSpec("max", unique=False, dropna=True)),
                },
                [["b", "b", "b", "b"], [None, None, None, None]],
                ["b1", "b2", "b3", "b4"],
            )

        def test_agg_count(self):
            def assert_eq(df, gp_keys, gp_map, expected, expected_cols):
                res = self.to_pandas_df(self.op.group_agg(df, gp_keys, gp_map))
                assert_df_eq(res, expected, expected_cols)

            pdf = self.to_df([[0, 1], [0, 1], [0, 4], [1, None], [0, None]], ["a", "b"])
            # count on single column
            assert_eq(
                pdf,
                ["a"],
                {
                    "b1": ("b", AggFunctionSpec("count", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("count", unique=True, dropna=False)),
                    "b3": ("b", AggFunctionSpec("count", unique=False, dropna=True)),
                    "b4": ("b", AggFunctionSpec("count", unique=True, dropna=True)),
                },
                [[4, 3, 3, 2], [1, 1, 0, 0]],
                ["b1", "b2", "b3", "b4"],
            )
            # count on all columns with nulls
            assert_eq(
                pdf,
                ["a"],
                {
                    "b1": ("*", AggFunctionSpec("count", unique=False, dropna=False)),
                    "b2": ("*", AggFunctionSpec("count", unique=True, dropna=False)),
                },
                [[4, 3], [1, 1]],
                ["b1", "b2"],
            )
            # count on keys with nulls
            assert_eq(
                pdf,
                ["b"],
                {
                    "a1": ("*", AggFunctionSpec("count", unique=False, dropna=False)),
                    "a2": ("*", AggFunctionSpec("count", unique=True, dropna=False)),
                },
                [[2, 2], [2, 1], [1, 1]],
                ["a1", "a2"],
            )
            # count multiple cols
            pdf = self.to_df(
                [
                    [0, 1, None],
                    [0, 1, None],
                    [0, 4, 1],
                    [1, None, None],
                    [None, None, None],
                ],
                ["a", "b", "c"],
            )
            assert_eq(
                pdf,
                ["a"],
                {
                    "a1": ("b,c", AggFunctionSpec("count", unique=False, dropna=False)),
                    "a2": ("b,c", AggFunctionSpec("count", unique=True, dropna=False)),
                },
                [[3, 2], [1, 1], [1, 1]],
                ["a1", "a2"],
            )

        def test_agg_combined(self):
            def assert_eq(df, gp_keys, gp_map, expected, expected_cols):
                res = self.to_pandas_df(self.op.group_agg(df, gp_keys, gp_map))
                assert_df_eq(res, expected, expected_cols)

            # combined case
            pdf = self.to_df(
                [
                    [0, 1, None],
                    [0, 1, None],
                    [0, 4, 1],
                    [1, None, None],
                    [None, None, None],
                ],
                ["a", "b", "c"],
            )
            assert_eq(
                pdf,
                ["a"],
                {
                    "a1": ("a", AggFunctionSpec("sum", unique=False, dropna=False)),
                    "a2": ("*", AggFunctionSpec("count", unique=True, dropna=False)),
                    "a3": ("c", AggFunctionSpec("sum", unique=True, dropna=False)),
                    "a4": ("*", AggFunctionSpec("count", unique=False, dropna=False)),
                    "a5": ("c", AggFunctionSpec("min", unique=False, dropna=False)),
                    "a6": ("b,c", AggFunctionSpec("count", unique=True, dropna=False)),
                },
                [
                    [0.0, 2.0, 1, 3.0, 1.0, 2.0],
                    [1.0, 1.0, None, 1.0, None, 1.0],
                    [None, 1.0, None, 1.0, None, 1.0],
                ],
                ["a1", "a2", "a3", "a4", "a5", "a6"],
            )

        def test_agg_no_group_first_last(self):
            def assert_eq(df, gp_map, expected, expected_cols):
                res = self.to_pandas_df(self.op.group_agg(df, [], gp_map))
                assert_df_eq(res, expected, expected_cols)

            pdf = self.to_df([[0, 1], [0, 1], [1, None], [1, 5], [0, None]], ["a", "b"])
            assert_eq(
                pdf,
                {
                    "b1": ("b", AggFunctionSpec("first", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("first", unique=False, dropna=True)),
                    "b3": ("b", AggFunctionSpec("last", unique=False, dropna=False)),
                    "b4": ("b", AggFunctionSpec("last", unique=False, dropna=True)),
                },
                [[1.0, 1.0, None, 5.0]],
                ["b1", "b2", "b3", "b4"],
            )

        def test_agg_no_group_sum(self):
            def assert_eq(df, gp_map, expected, expected_cols):
                res = self.to_pandas_df(self.op.group_agg(df, [], gp_map))
                assert_df_eq(res, expected, expected_cols)

            pdf = self.to_df([[0, 1], [0, 1], [1, None], [1, 5], [0, None]], ["a", "b"])
            assert_eq(
                pdf,
                {
                    "b1": ("b", AggFunctionSpec("sum", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("sum", unique=True, dropna=False)),
                    "b3": ("b", AggFunctionSpec("sum", unique=True, dropna=True)),
                    "b4": ("b", AggFunctionSpec("sum", unique=False, dropna=True)),
                },
                [[7, 6, 6, 7]],
                ["b1", "b2", "b3", "b4"],
            )

        def test_agg_no_group_min_max(self):
            def assert_eq(df, gp_map, expected, expected_cols):
                res = self.to_pandas_df(self.op.group_agg(df, [], gp_map))
                assert_df_eq(res, expected, expected_cols)

            pdf = self.to_df([[0, 1], [0, 1], [1, None], [1, 5], [0, None]], ["a", "b"])
            assert_eq(
                pdf,
                {
                    "b1": ("b", AggFunctionSpec("min", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("min", unique=True, dropna=False)),
                    "b3": ("b", AggFunctionSpec("min", unique=True, dropna=True)),
                    "b4": ("b", AggFunctionSpec("min", unique=False, dropna=True)),
                },
                [[1.0, 1.0, 1.0, 1.0]],
                ["b1", "b2", "b3", "b4"],
            )
            assert_eq(
                pdf,
                {
                    "b1": ("b", AggFunctionSpec("max", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("max", unique=True, dropna=False)),
                    "b3": ("b", AggFunctionSpec("max", unique=True, dropna=True)),
                    "b4": ("b", AggFunctionSpec("max", unique=False, dropna=True)),
                },
                [[5, 5, 5, 5]],
                ["b1", "b2", "b3", "b4"],
            )

        def test_agg_no_group_mean(self):
            def assert_eq(df, gp_map, expected, expected_cols):
                res = self.to_pandas_df(self.op.group_agg(df, [], gp_map))
                assert_df_eq(res, expected, expected_cols)

            pdf = self.to_df([[0, 1], [0, 1], [0, 4], [0, None]], ["a", "b"])
            assert_eq(
                pdf,
                {
                    "b1": ("b", AggFunctionSpec("avg", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("avg", unique=True, dropna=False)),
                    "b3": ("b", AggFunctionSpec("mean", unique=True, dropna=True)),
                    "b4": ("b", AggFunctionSpec("mean", unique=False, dropna=True)),
                },
                [[2, 2.5, 2.5, 2]],
                ["b1", "b2", "b3", "b4"],
            )

        def test_agg_no_group_count(self):
            def assert_eq(df, gp_map, expected, expected_cols):
                res = self.to_pandas_df(self.op.group_agg(df, [], gp_map))
                assert_df_eq(res, expected, expected_cols)

            pdf = self.to_df([[0, 1], [0, 1], [1, None]], ["a", "b"])
            # count on single column
            assert_eq(
                pdf,
                {
                    "b1": ("b", AggFunctionSpec("count", unique=False, dropna=False)),
                    "b2": ("b", AggFunctionSpec("count", unique=True, dropna=False)),
                    "b3": ("b", AggFunctionSpec("count", unique=False, dropna=True)),
                    "b4": ("b", AggFunctionSpec("count", unique=True, dropna=True)),
                },
                [[3, 2, 2, 1]],
                ["b1", "b2", "b3", "b4"],
            )
            # count on all columns with nulls
            assert_eq(
                pdf,
                {
                    "b1": ("*", AggFunctionSpec("count", unique=False, dropna=False)),
                    "b2": ("*", AggFunctionSpec("count", unique=True, dropna=False)),
                },
                [[3, 2]],
                ["b1", "b2"],
            )
            # count multiple cols
            pdf = self.to_df(
                [
                    [0, 1, None],
                    [0, 1, None],
                    [0, 4, 1],
                    [1, None, None],
                    [None, None, None],
                ],
                ["a", "b", "c"],
            )
            assert_eq(
                pdf,
                {
                    "a1": ("b,c", AggFunctionSpec("count", unique=False, dropna=False)),
                    "a2": ("b,c", AggFunctionSpec("count", unique=True, dropna=False)),
                },
                [[5, 3]],
                ["a1", "a2"],
            )

        def test_agg_no_group_combined(self):
            def assert_eq(df, gp_map, expected, expected_cols):
                res = self.to_pandas_df(self.op.group_agg(df, [], gp_map))
                assert_df_eq(res, expected, expected_cols)

            pdf = self.to_df(
                [
                    [0, 1, None],
                    [0, 1, None],
                    [0, 4, 1],
                    [1, None, None],
                    [None, None, None],
                ],
                ["a", "b", "c"],
            )
            # combo test
            assert_eq(
                pdf,
                {
                    "a1": ("b,c", AggFunctionSpec("count", unique=False, dropna=False)),
                    "a2": ("*", AggFunctionSpec("count", unique=True, dropna=False)),
                    "a3": ("a", AggFunctionSpec("first", unique=True, dropna=False)),
                    "a4": ("b", AggFunctionSpec("max", unique=True, dropna=False)),
                },
                [[5, 4, 0, 4]],
                ["a1", "a2", "a3", "a4"],
            )

        def test_window_row_number(self):
            def make_func(partition_keys, order_by):
                ws = WindowSpec(
                    "",
                    partition_keys=partition_keys,
                    order_by=OrderBySpec(*order_by),
                    windowframe=make_windowframe_spec(""),
                )
                return WindowFunctionSpec("row_number", False, False, ws)

            a = self.to_df([[0, 1], [0, 2]], ["a", "b"])
            self.w_eq(
                a, make_func([], []), [], "x", [[0, 1, 1], [0, 2, 2]], ["a", "b", "x"]
            )
            self.w_eq(
                a,
                make_func([], [("a", True), ("b", False)]),
                [],
                "x",
                [[0, 1, 2], [0, 2, 1]],
                ["a", "b", "x"],
            )
            a = self.to_df([[0, 1], [0, None], [None, 1], [None, None]], ["a", "b"])
            self.w_eq(
                a,
                make_func([], [("a", True), ("b", True)]),
                [],
                "x",
                [[0, 1, 4], [0, None, 3], [None, 1, 2], [None, None, 1]],
                ["a", "b", "x"],
            )
            self.w_eq(
                a,
                make_func([], [("a", True, "last"), ("b", True, "last")]),
                [],
                "x",
                [[0, 1, 1], [0, None, 2], [None, 1, 3], [None, None, 4]],
                ["a", "b", "x"],
            )
            a = self.to_df([[0, 1], [0, 4], [2, 3]], ["a", "b"])
            self.w_eq(
                a,
                make_func([], [("b", False)]),
                [],
                "x",
                [[0, 1, 3], [0, 4, 1], [2, 3, 2]],
                ["a", "b", "x"],
            )

        def test_window_row_number_partition_by(self):
            def make_func(partition_keys, order_by):
                ws = WindowSpec(
                    "",
                    partition_keys=partition_keys,
                    order_by=OrderBySpec(*order_by),
                    windowframe=make_windowframe_spec(""),
                )
                return WindowFunctionSpec("row_number", False, False, ws)

            a = self.to_df([[0, 1], [0, None], [None, 1], [None, None]], ["a", "b"])
            self.w_eq(
                a,
                make_func(["a"], [("a", True), ("b", True)]),
                [],
                "x",
                [[0, 1, 2], [0, None, 1], [None, 1, 2], [None, None, 1]],
                ["a", "b", "x"],
            )

        def test_window_ranks(self):
            def make_func(func, partition_keys, order_by):
                ws = WindowSpec(
                    "",
                    partition_keys=partition_keys,
                    order_by=OrderBySpec(*order_by),
                    windowframe=make_windowframe_spec(""),
                )
                return WindowFunctionSpec(func, False, False, ws)

            a = self.to_df([[0, 1], [0, 1], [None, 1], [0, None]], ["a", "b"])
            self.w_eq(
                a,
                make_func("rank", [], ["b"]),
                [],
                "x",
                [[0, 1, 2], [0, 1, 2], [None, 1, 2], [0, None, 1]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("rank", [], [("b", False)]),
                [],
                "x",
                [[0, 1, 1], [0, 1, 1], [None, 1, 1], [0, None, 4]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("dense_rank", [], ["b"]),
                [],
                "x",
                [[0, 1, 2], [0, 1, 2], [None, 1, 2], [0, None, 1]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("dense_rank", [], [("b", False)]),
                [],
                "x",
                [[0, 1, 1], [0, 1, 1], [None, 1, 1], [0, None, 2]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("percentile_rank", [], ["b"]),
                [],
                "x",
                [
                    [0, 1, 0.33333333333],
                    [0, 1, 0.33333333333],
                    [None, 1, 0.33333333333],
                    [0, None, 0.0],
                ],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("percentile_rank", [], [("b", False)]),
                [],
                "x",
                [[0, 1, 0.0], [0, 1, 0.0], [None, 1, 0.0], [0, None, 1.0]],
                ["a", "b", "x"],
            )

        def test_window_ranks_partition_by(self):
            def make_func(func, partition_keys, order_by):
                ws = WindowSpec(
                    "",
                    partition_keys=partition_keys,
                    order_by=OrderBySpec(*order_by),
                    windowframe=make_windowframe_spec(""),
                )
                return WindowFunctionSpec(func, False, False, ws)

            a = self.to_df([[0, 1], [0, 1], [None, 1], [0, None]], ["a", "b"])
            self.w_eq(
                a,
                make_func("rank", ["a"], ["b"]),
                [],
                "x",
                [[0, 1, 2], [0, 1, 2], [None, 1, 1], [0, None, 1]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("rank", ["a"], [("b", False)]),
                [],
                "x",
                [[0, 1, 1], [0, 1, 1], [None, 1, 1], [0, None, 3]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("dense_rank", ["a"], ["b"]),
                [],
                "x",
                [[0, 1, 2], [0, 1, 2], [None, 1, 1], [0, None, 1]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("dense_rank", ["a"], [("b", False)]),
                [],
                "x",
                [[0, 1, 1], [0, 1, 1], [None, 1, 1], [0, None, 2]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("percentile_rank", ["a"], ["b"]),
                [],
                "x",
                [[0, 1, 0.5], [0, 1, 0.5], [None, 1, 0.0], [0, None, 0.0]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("percentile_rank", ["a"], [("b", False)]),
                [],
                "x",
                [[0, 1, 0.0], [0, 1, 0.0], [None, 1, 0.0], [0, None, 1.0]],
                ["a", "b", "x"],
            )

        def test_window_lead_lag(self):
            def make_func(func, partition_keys, order_by):
                ws = WindowSpec(
                    "",
                    partition_keys=partition_keys,
                    order_by=OrderBySpec(*order_by),
                    windowframe=make_windowframe_spec(""),
                )
                return WindowFunctionSpec(func, False, False, ws)

            a = self.to_df([[0, 1], [0, 1], [None, 1], [0, None]], ["a", "b"])
            self.w_eq(
                a,
                make_func("lag", [], []),
                [col("b"), 1],
                "x",
                [[0, 1, None], [0, 1, 1], [None, 1, 1], [0, None, 1]],
                ["a", "b", "x"],
            )
            self.w_eq(
                a,
                make_func("lag", [], []),
                [col("b"), 1, 100],
                "x",
                [[0, 1, 100], [0, 1, 1], [None, 1, 1], [0, None, 1]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("lead", [], []),
                [col("b"), 1],
                "x",
                [[0, 1, 1], [0, 1, 1], [None, 1, None], [0, None, None]],
                ["a", "b", "x"],
            )
            self.w_eq(
                a,
                make_func("lead", [], []),
                [col("b"), 1, 100],
                "x",
                [[0, 1, 1], [0, 1, 1], [None, 1, None], [0, None, 100]],
                ["a", "b", "x"],
            )

        def test_window_lead_lag_partition_by(self):
            def make_func(func, partition_keys, order_by):
                ws = WindowSpec(
                    "",
                    partition_keys=partition_keys,
                    order_by=OrderBySpec(*order_by),
                    windowframe=make_windowframe_spec(""),
                )
                return WindowFunctionSpec(func, False, False, ws)

            a = self.to_df([[0, 1], [0, 1], [None, 1], [0, None]], ["a", "b"])
            self.w_eq(
                a,
                make_func("lag", ["a"], ["b"]),
                [col("b"), 1],
                "x",
                [[0, 1, None], [0, 1, 1], [None, 1, None], [0, None, None]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("lead", ["a"], ["b"]),
                [col("b"), 1],
                "x",
                [[0, 1, 1], [0, 1, None], [None, 1, None], [0, None, 1]],
                ["a", "b", "x"],
            )

        def test_window_sum(self):
            def make_func(partition_keys, order_by, start=None, end=None):
                wtype = "" if start is None and end is None else "rows"
                ws = WindowSpec(
                    "",
                    partition_keys=partition_keys,
                    order_by=OrderBySpec(*order_by),
                    windowframe=make_windowframe_spec(wtype, start, end),
                )
                return WindowFunctionSpec("sum", False, False, ws)

            a = self.to_df([[0, 1], [0, 2]], ["a", "b"])
            # no partition no window frame
            self.w_eq(
                a,
                make_func([], []),
                [col("b")],
                "x",
                [[0, 1, 3], [0, 2, 3]],
                ["a", "b", "x"],
            )
            self.w_eq(
                a,
                make_func([], [("a", True), ("b", False)]),
                [col("b")],
                "x",
                [[0, 1, 3], [0, 2, 3]],
                ["a", "b", "x"],
            )

            a = self.to_df([[0, 1], [None, 1], [0, None], [0, 2]], ["a", "b"])
            # expanding, no partition
            self.w_eq(
                a,
                make_func([], ["b", "a"], end=0),
                [col("b")],
                "x",
                [[0, 1, 2], [None, 1, 1], [0, None, None], [0, 2, 4]],
                ["a", "b", "x"],
            )

            # rolling, no partition
            self.w_eq(
                a,
                make_func([], ["b", "a"], start=-1, end=0),
                [col("b")],
                "x",
                [[0, 1, 2], [None, 1, 1], [0, None, None], [0, 2, 3]],
                ["a", "b", "x"],
            )

            if not pd.__version__.startswith("1.1"):
                # irregular, no partition
                self.w_eq(
                    a,
                    make_func([], ["b", "a"], end=-1),
                    [col("b")],
                    "x",
                    [[0, 1, 1], [None, 1, None], [0, None, None], [0, 2, 2]],
                    ["a", "b", "x"],
                )

                # irregular, no partition
                self.w_eq(
                    a,
                    make_func([], ["b", "a"], start=-2, end=-1),
                    [col("b")],
                    "x",
                    [[0, 1, 1], [None, 1, None], [0, None, None], [0, 2, 2]],
                    ["a", "b", "x"],
                )

                # irregular, no partition
                self.w_eq(
                    a,
                    make_func([], ["b", "a"], start=1, end=None),
                    [col("b")],
                    "x",
                    [[0, 1, 2], [None, 1, 3], [0, None, 4], [0, 2, None]],
                    ["a", "b", "x"],
                )

        def test_window_sum_partition_by(self):
            def make_func(partition_keys, order_by, start=None, end=None):
                wtype = "" if start is None and end is None else "rows"
                ws = WindowSpec(
                    "",
                    partition_keys=partition_keys,
                    order_by=OrderBySpec(*order_by),
                    windowframe=make_windowframe_spec(wtype, start, end),
                )
                return WindowFunctionSpec("sum", False, False, ws)

            # no partition no window frame
            # partition no window frame
            a = self.to_df([[0, 1], [None, 1], [0, None], [0, 2]], ["a", "b"])
            self.w_eq(
                a,
                make_func(["a"], []),
                [col("b")],
                "x",
                [[0, 1, 3], [None, 1, 1], [0, None, 3], [0, 2, 3]],
                ["a", "b", "x"],
            )

            # expanding, with partition
            self.w_eq(
                a,
                make_func(["a"], ["b", "a"], end=0),
                [col("b")],
                "x",
                [[0, 1, 1], [None, 1, 1], [0, None, None], [0, 2, 3]],
                ["a", "b", "x"],
            )

            # rolling, with partition
            self.w_eq(
                a,
                make_func(["a"], ["b", "a"], start=-1, end=0),
                [col("b")],
                "x",
                [[0, 1, 1], [None, 1, 1], [0, None, None], [0, 2, 3]],
                ["a", "b", "x"],
            )
            self.w_eq(
                a,
                make_func(["a"], ["b", "a"], start=0, end=0),
                [col("b")],
                "x",
                [[0, 1, 1], [None, 1, 1], [0, None, None], [0, 2, 2]],
                ["a", "b", "x"],
            )

            if not pd.__version__.startswith("1.1"):
                # irregular, with partition
                self.w_eq(
                    a,
                    make_func(["a"], ["b"], end=-1),
                    [col("b")],
                    "x",
                    [[0, 1, None], [None, 1, None], [0, None, None], [0, 2, 1]],
                    ["a", "b", "x"],
                )

                # irregular, with partition
                self.w_eq(
                    a,
                    make_func(["a"], ["b"], start=-1, end=-1),
                    [col("b")],
                    "x",
                    [[0, 1, None], [None, 1, None], [0, None, None], [0, 2, 1]],
                    ["a", "b", "x"],
                )

                # irregular, with partition
                self.w_eq(
                    a,
                    make_func(["a"], ["b"], start=1, end=None),
                    [col("b")],
                    "x",
                    [[0, 1, 2], [None, 1, None], [0, None, 3], [0, 2, None]],
                    ["a", "b", "x"],
                )

        def test_window_simple_agg_partition_by(self):
            def make_func(func, partition_keys, order_by, start=None, end=None):
                wtype = "" if start is None and end is None else "rows"
                ws = WindowSpec(
                    "",
                    partition_keys=partition_keys,
                    order_by=OrderBySpec(*order_by),
                    windowframe=make_windowframe_spec(wtype, start, end),
                )
                return WindowFunctionSpec(func, False, False, ws)

            a = self.to_df([[0, 1], [None, 1], [0, None], [0, 2]], ["a", "b"])
            self.w_eq(
                a,
                make_func("max", ["a"], ["b"]),
                [col("b")],
                "x",
                [[0, 1, 2], [None, 1, 1], [0, None, 2], [0, 2, 2]],
                ["a", "b", "x"],
            )
            self.w_eq(
                a,
                make_func("max", ["a"], ["b"], start=-1, end=0),
                [col("b")],
                "x",
                [[0, 1, 1], [None, 1, 1], [0, None, None], [0, 2, 2]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("min", ["a"], ["b"]),
                [col("b")],
                "x",
                [[0, 1, 1], [None, 1, 1], [0, None, 1], [0, 2, 1]],
                ["a", "b", "x"],
            )
            self.w_eq(
                a,
                make_func("min", ["a"], ["b"], start=-1, end=0),
                [col("b")],
                "x",
                [[0, 1, 1], [None, 1, 1], [0, None, None], [0, 2, 1]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("avg", ["a"], ["b"]),
                [col("b")],
                "x",
                [[0, 1, 1.5], [None, 1, 1], [0, None, 1.5], [0, 2, 1.5]],
                ["a", "b", "x"],
            )
            self.w_eq(
                a,
                make_func("mean", ["a"], ["b"], start=-1, end=0),
                [col("b")],
                "x",
                [[0, 1, 1.0], [None, 1, 1], [0, None, None], [0, 2, 1.5]],
                ["a", "b", "x"],
            )

            self.w_eq(
                a,
                make_func("count", ["a"], ["b"]),
                [col("b")],
                "x",
                [[0, 1, 2], [None, 1, 1], [0, None, 2], [0, 2, 2]],
                ["a", "b", "x"],
            )
            a = self.to_df([[0, 1], [None, 1], [0, None], [0, 3]], ["a", "b"])
            self.w_eq(
                a,
                make_func("count", ["a"], [("b", True)], start=-1, end=0),
                [col("b")],
                "x",
                [[0, 1, 1], [None, 1, 1], [0, None, 0], [0, 3, 2]],
                ["a", "b", "x"],
            )

        def w_eq(self, df, func, cols, dest, expected, expected_cols):
            cols = [
                x if isinstance(x, ArgumentSpec) else ArgumentSpec(False, x)
                for x in cols
            ]
            res = self.to_pandas_df(self.op.window(df, func, cols, dest))
            assert_df_eq(res, expected, expected_cols)


def col(name):
    return ArgumentSpec(True, name)
