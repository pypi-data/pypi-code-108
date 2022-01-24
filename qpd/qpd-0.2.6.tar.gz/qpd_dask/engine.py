from typing import Any, Callable, Dict, List, Tuple

import dask.array as np
import dask.dataframe as pd
import numpy
import pandas
from qpd import PandasLikeUtils, QPDEngine, run_sql
from qpd.dataframe import Column, DataFrame
from qpd.specs import (
    AggFunctionSpec,
    ArgumentSpec,
    OrderBySpec,
    RollingWindowFrame,
    WindowFunctionSpec,
)
from qpd_pandas.engine import _RowsIndexer
from triad.utils.assertion import assert_or_throw


def run_sql_on_dask(
    sql: str, dfs: Dict[str, Any], ignore_case: bool = False
) -> pd.DataFrame:
    return run_sql(QPDDaskEngine(), sql, dfs, ignore_case=ignore_case)


class DaskUtils(PandasLikeUtils[pd.DataFrame, pd.Series]):
    pass


class QPDDaskEngine(QPDEngine):
    @property
    def pl_utils(self) -> DaskUtils:
        return DaskUtils()

    def to_df(self, obj: Any) -> DataFrame:
        if isinstance(obj, DataFrame):
            return obj
        if isinstance(obj, pandas.DataFrame):
            df = pd.from_pandas(obj, npartitions=2)  # TODO: don't hard code
            return DataFrame(Column(df[x], x) for x in df.columns.tolist())
        if isinstance(obj, pd.DataFrame):
            return DataFrame(Column(obj[x], x) for x in obj.columns.tolist())
        raise ValueError(f"{obj} is not supported")  # pragma: no cover

    def to_col(self, value: Any, name: str = "") -> Column:
        if isinstance(value, list):
            pdf = pandas.DataFrame({name: value})
            ddf = pd.from_pandas(pdf, npartitions=2)
            return Column(ddf[name], name)
        return Column(value, name)

    def to_native(self, df: DataFrame) -> Any:
        if all(not self.is_series(x.native) for x in df.values()):
            return pd.from_pandas(
                pandas.DataFrame({k: [v.native] for k, v in df.items()}), npartitions=2
            )
        values = {k: v.native for k, v in df.items() if not self.is_series(v.native)}
        series = [v.native.rename(k) for k, v in df.items() if self.is_series(v.native)]
        assert_or_throw(
            len(series) > 0, ValueError("DataFrame doesn't contain any series")
        )
        ddf = series[0].to_frame()
        for s in series[1:]:
            ddf[s.name] = s
        for k, v in values.items():
            ddf[k] = v
        return ddf[list(df.keys())]

    def is_series(self, obj: Any) -> bool:
        return isinstance(obj, pd.Series)

    def case_when(self, *cols: Column) -> Column:
        """`cols` must be in the format of
        `when1`, `value1`, ... ,`default`, and length must be >= 3.
        The reason to design the interface in this way is to simplify the translation
        from SQL to engine APIs.

        :return: [description]
        :rtype: Column
        """
        assert_or_throw(len(cols) >= 3, "case when must have 1+ conditions")

        # construct a new dataframe with all conditions and values
        # we have to do this to keep all series/consts with the same dimension
        # dask array where will lose shape info
        # so we have to make this operation on dataframe
        series: List[Tuple[int, pd.Series]] = []
        values: List[Tuple[int, Any]] = []
        for i in range(len(cols)):
            if self.is_series(cols[i].native):
                series.append((i, cols[i].native))
            else:
                values.append((i, cols[i].native))
        assert_or_throw(
            len(series) > 0, ValueError("DataFrame doesn't contain any series")
        )
        ddf = series[0][1].to_frame(name=str(series[0][0]))
        for i, s in series[1:]:
            ddf[str(i)] = s
        for i, v in values:
            ddf[str(i)] = v

        # adding masks backwards
        pos = len(cols) - 1
        result = ddf[str(pos)]
        pos -= 2
        while pos >= 0:
            result = result.mask(self._safe_bool(ddf[str(pos)]) > 0, ddf[str(pos + 1)])
            pos -= 2
        return Column(result)

    def order_by_limit(
        self, df: DataFrame, order_by: OrderBySpec, limit: int
    ) -> DataFrame:
        assert_or_throw(
            not (len(order_by) > 0 and limit < 0),
            ValueError("for dask engine, limit is required by order by"),
        )
        if len(order_by) == 0 and limit < 0:  # pragma: no cover
            return df
        ndf = self.to_native(df)
        if len(order_by) == 0 or limit == 0:
            return self.to_df(ndf.head(limit, npartitions=-1, compute=False))

        ndf, sort_keys, asc = self._prepare_sort(ndf, order_by)

        def p_apply(df: Any) -> Any:
            return df.sort_values(sort_keys, ascending=asc).head(limit)

        meta = [(ndf[x].name, ndf[x].dtype) for x in ndf.columns]
        res = ndf.map_partitions(p_apply, meta=meta).compute()
        res = res.sort_values(sort_keys, ascending=asc).head(limit)
        return self.to_df(res[list(df.keys())])

    def group_agg(
        self,
        df: DataFrame,
        keys: List[str],
        agg_map: Dict[str, Tuple[str, AggFunctionSpec]],
    ) -> DataFrame:
        if len(keys) > 0:
            return self._group_agg_with_keys(df, keys, agg_map)
        else:
            return self._group_agg_no_keys(df, agg_map)

    def window(  # noqa: C901
        self,
        df: DataFrame,
        func: WindowFunctionSpec,
        args: List[ArgumentSpec],
        dest_col_name: str,
    ) -> DataFrame:
        if func.name == "row_number":
            return self._window_row_number(df, func, args, dest_col_name)
        if func.name == "sum":
            return self._window_simple_agg(
                lambda x: x.sum(min_count=1), df, func, args, dest_col_name
            )
        if func.name == "min":
            return self._window_simple_agg(
                lambda x: x.min(), df, func, args, dest_col_name
            )
        if func.name == "max":
            return self._window_simple_agg(
                lambda x: x.max(), df, func, args, dest_col_name
            )
        if func.name == "count":
            return self._window_simple_agg(
                lambda x: x.count(), df, func, args, dest_col_name
            )
        if func.name in ["avg", "mean"]:
            return self._window_simple_agg(
                lambda x: x.mean(), df, func, args, dest_col_name
            )
        if func.name in ["rank"]:
            return self._window_ranks(
                lambda x: x.rank(method="min"), df, func, args, dest_col_name
            )
        if func.name in ["dense_rank"]:
            return self._window_ranks(
                lambda x: x.rank(method="dense"), df, func, args, dest_col_name
            )
        if func.name in ["percentile_rank", "percent_rank"]:

            def pct_rank(s: Any) -> Any:
                m = s.size - 1
                ranks = s.rank(method="min") - 1
                if m == 0:
                    m = 1.0
                return ranks / m

            return self._window_ranks(
                lambda x: pct_rank(x)
                if isinstance(x, pandas.Series)
                else x.apply(pct_rank),
                df,
                func,
                args,
                dest_col_name,
            )
        if func.name == "lead":
            return self._window_lead_lag(
                lambda x, delta, default: x.shift(-delta, fill_value=default),
                df,
                func,
                args,
                dest_col_name,
            )
        if func.name == "lag":
            return self._window_lead_lag(
                lambda x, delta, default: x.shift(delta, fill_value=default),
                df,
                func,
                args,
                dest_col_name,
            )
        raise NotImplementedError(f"{func}")  # pragma: no cover

    def _window_row_number(
        self,
        df: DataFrame,
        func: WindowFunctionSpec,
        args: List[ArgumentSpec],
        dest_col_name: str,
    ) -> DataFrame:
        assert_or_throw(len(args) == 0, ValueError(f"{args}"))
        assert_or_throw(
            not func.has_windowframe, ValueError("row_number can't have windowframe")
        )
        assert_or_throw(
            not (func.has_order_by and not func.has_partition_by),
            ValueError("for dask engine, order by requires partition by"),
        )
        assert_or_throw(
            func.has_partition_by,
            ValueError("for dask engine, partition by is required for row_number()"),
        )
        keys = list(df.keys())
        ndf = self.to_native(df)
        ndf, sort_keys, asc = self._prepare_sort(ndf, func.window.order_by)
        gp, gp_keys, _ = self._safe_groupby(ndf, func.window.partition_keys)
        if not func.has_order_by:  # pragma: no cover
            # unable to have deterministic test
            col = gp.cumcount() + 1
            ndf[dest_col_name] = col
            return self.to_df(ndf[keys + [dest_col_name]])

        def gp_apply(df: Any) -> Any:
            df = df.sort_values(sort_keys, ascending=asc)
            col = np.arange(1, 1 + df.shape[0])
            df[dest_col_name] = col
            return df.reset_index(drop=True)

        meta = [(ndf[x].name, ndf[x].dtype) for x in ndf.columns]
        meta += [(dest_col_name, "int64")]

        ndf = gp.apply(gp_apply, meta=meta).reset_index(drop=True)
        return self.to_df(ndf[keys + [dest_col_name]])

    def _window_ranks(
        self,
        rank_func: Callable,
        df: DataFrame,
        func: WindowFunctionSpec,
        args: List[ArgumentSpec],
        dest_col_name: str,
    ) -> DataFrame:
        assert_or_throw(len(args) == 0, ValueError(f"{args}"))
        assert_or_throw(
            func.has_order_by, ValueError(f"rank functions require order by {func}")
        )
        assert_or_throw(
            not func.has_windowframe,
            ValueError(f"rank functions can't have windowframe {func}"),
        )
        assert_or_throw(
            not (func.has_order_by and not func.has_partition_by),
            ValueError("for dask engine, order by requires partition by"),
        )
        assert_or_throw(
            func.has_partition_by,
            ValueError("for dask engine, partition by is required for ranking"),
        )
        ndf = self.to_native(df)
        keys = list(df.keys())
        ndf, sort_keys, asc = self._prepare_sort(ndf, func.window.order_by)
        gp, gp_keys, _ = self._safe_groupby(ndf, func.window.partition_keys)

        def gp_apply(gdf: Any) -> Any:
            gdf = gdf.sort_values(sort_keys, ascending=asc)
            rank_on = self._safe_pandas_groupby(
                gdf, sort_keys, as_index=False, sort=False
            )[0].ngroup()
            gdf[dest_col_name] = rank_func(rank_on)
            return gdf.reset_index(drop=True)

        meta = [(ndf[x].name, ndf[x].dtype) for x in ndf.columns]
        meta += [(dest_col_name, "f8")]

        ndf = gp.apply(gp_apply, meta=meta).reset_index(drop=True)
        return self.to_df(ndf[keys + [dest_col_name]])

    def _window_lead_lag(
        self,
        l_func: Callable,
        df: DataFrame,
        func: WindowFunctionSpec,
        args: List[ArgumentSpec],
        dest_col_name: str,
    ) -> DataFrame:
        assert_or_throw(
            not (func.has_order_by and not func.has_partition_by),
            ValueError("for dask engine, order by requires partition by"),
        )
        assert_or_throw(
            func.has_partition_by,
            ValueError("for dask engine, partition by is required for lead/lag"),
        )
        assert_or_throw(len(args) in [2, 3], ValueError(f"{args}"))
        assert_or_throw(args[0].is_col, ValueError(f"{args[0]}"))
        assert_or_throw(
            not args[1].is_col and isinstance(args[1].value, int),
            ValueError(f"{args[1]}"),
        )
        if len(args) == 3:
            assert_or_throw(not args[2].is_col, ValueError(f"{args[2]}"))
        assert_or_throw(
            not func.has_windowframe,
            ValueError(f"lead/lag functions can't have windowframe {func}"),
        )
        col = args[0].value
        delta = int(args[1].value)
        default = None if len(args) == 2 else args[2].value

        ndf = self.to_native(df)
        keys = list(df.keys())
        ndf, sort_keys, asc = self._prepare_sort(ndf, func.window.order_by)
        gp, gp_keys, _ = self._safe_groupby(ndf, func.window.partition_keys)

        def gp_apply(gdf: Any) -> Any:
            gdf = gdf.sort_values(sort_keys, ascending=asc)
            gdf[dest_col_name] = l_func(gdf[col], delta, default)
            return gdf.reset_index(drop=True)

        meta = [(ndf[x].name, ndf[x].dtype) for x in ndf.columns]
        meta += [(dest_col_name, ndf[col].dtype)]

        ndf = gp.apply(gp_apply, meta=meta).reset_index(drop=True)
        return self.to_df(ndf[keys + [dest_col_name]])

    def _window_simple_agg(  # noqa: C901
        self,
        agg_func: Callable,
        df: DataFrame,
        func: WindowFunctionSpec,
        args: List[ArgumentSpec],
        dest_col_name: str,
    ) -> DataFrame:
        assert_or_throw(
            not (func.has_order_by and not func.has_partition_by),
            ValueError("for dask engine, order by requires partition by"),
        )
        assert_or_throw(
            func.has_partition_by,
            ValueError(
                "for dask engine, partition by is required for window aggregation"
            ),
        )
        assert_or_throw(len(args) == 1 and args[0].is_col, ValueError(f"{args}"))
        assert_or_throw(
            not func.unique and not func.dropna,
            NotImplementedError(
                f"window function doesn't support unique {func.unique} "
                + f"and dropna {func.dropna}"
            ),
        )
        col = args[0].value

        ndf = self.to_native(df)
        keys = list(df.keys())
        ndf, sort_keys, asc = self._prepare_sort(ndf, func.window.order_by)
        gp, gp_keys, mi = self._safe_groupby(ndf, func.window.partition_keys)

        def gp_apply(gdf: Any) -> Any:
            if len(sort_keys) > 0:
                gdf = gdf.sort_values(sort_keys, ascending=asc)
            if not func.has_windowframe:
                res: Any = agg_func(gdf[col])
            else:
                wf = func.window.windowframe
                assert_or_throw(
                    isinstance(wf, RollingWindowFrame), NotImplementedError(f"{wf}")
                )
                min_p = 0 if func.name in ["count", "min", "max"] else 1
                # 1.1.0 has this bug
                # https://github.com/pandas-dev/pandas/issues/35557
                # we try to use native functions here to bypass bugs
                if wf.start is None and wf.end == 0:
                    rolling_func: Callable = lambda x: x.expanding(min_periods=min_p)
                elif wf.window is not None and wf.end == 0:  # type: ignore
                    rolling_func: Callable = lambda x: x.rolling(  # type: ignore
                        window=wf.window, min_periods=min_p  # type: ignore
                    )
                else:  # will not work on version pandas 1.1.0  # pragma: no cover
                    rolling_func: Callable = lambda x: x.rolling(  # type: ignore
                        window=_RowsIndexer(wf.start, wf.end), min_periods=min_p
                    )
                res = agg_func(rolling_func(gdf[col]))
            gdf[dest_col_name] = res
            return gdf.reset_index(drop=True)

        meta = [(ndf[x].name, ndf[x].dtype) for x in ndf.columns]
        meta += [(dest_col_name, ndf[col].dtype)]

        ndf = gp.apply(gp_apply, meta=meta).reset_index(drop=True)
        return self.to_df(ndf[keys + [dest_col_name]])

    def _group_agg_with_keys(  # noqa: C901
        self,
        df: DataFrame,
        keys: List[str],
        agg_map: Dict[str, Tuple[str, AggFunctionSpec]],
    ) -> DataFrame:
        ndf = self.to_native(df)
        gp, gp_keys, mi = self._safe_groupby(ndf, keys)
        col_group1: List[pd.Series] = []
        col_group2: List[pd.Series] = []
        for k, v in agg_map.items():
            if "*" in v[0] or "," in v[0]:
                continue
            series, is_agg = self._agg_gp(v[1], gp[v[0]], ndf[v[0]].dtype, mi)
            series = series.rename(k)
            if is_agg:
                col_group1.append(series)
            else:  # different divisions, will need special handling...
                col_group2.append(series)
        for k, v in agg_map.items():
            if "*" in v[0] or "," in v[0]:
                if v[1].unique:
                    series = self._count_unique(ndf, gp_keys, v[0], v[1]).rename(k)
                    col_group2.append(series)
                else:
                    series = self._count_all(gp, v[1]).rename(k)
                    col_group1.append(series)
        res: Any = None
        if len(col_group1) > 0:
            res = col_group1[0].to_frame()
            for s in col_group1[1:]:
                res[s.name] = s
            # TODO: the index of group agg is incorrect in dask
            # otherwise, we can join by index, that can be faster
            res = res.reset_index()
        if len(col_group2) > 0:
            if res is None:
                res = col_group2[0].reset_index()
                n = 1
            else:
                n = 0
            for s in col_group2[n:]:
                tdf = s.reset_index()
                res = res.merge(tdf, "outer", on=gp_keys)
        assert_or_throw(res is not None, ValueError("No aggregation happened"))
        res = res.reset_index()
        res = res[list(agg_map.keys())]
        return self.to_df(res)

    def _group_agg_no_keys(
        self,
        df: DataFrame,
        agg_map: Dict[str, Tuple[str, AggFunctionSpec]],
    ) -> DataFrame:
        ndf = self.to_native(df)
        aggs: Dict[str, Any] = {}
        for k, v in agg_map.items():
            if "*" in v[0] or "," in v[0]:
                continue
            aggs[k] = self._agg_no_gp(v[1], ndf[v[0]])
        for k, v in agg_map.items():
            if "*" in v[0] or "," in v[0]:
                if v[1].unique:
                    aggs[k] = self._count_unique_no_group(ndf, v[0], v[1])
                else:
                    aggs[k] = self._count_all_no_group(ndf, v[1])
        data: Dict[str, Any] = {}
        for k, vv in aggs.items():
            s = vv.compute() if hasattr(vv, "compute") else vv
            if isinstance(s, pandas.Series):
                data[k] = [s.iloc[0]]
            else:
                data[k] = [s]
        return self.to_df(pandas.DataFrame(data))

    def _agg_gp(  # noqa: C901
        self, func: AggFunctionSpec, gp: Any, dtype: Any, index: pandas.MultiIndex
    ) -> Tuple[Any, bool]:
        # TODO: this function has compatibility issue with pandas < 1
        # for example: we want to compute the sum of a same column twice
        # https://github.com/pandas-dev/pandas/issues/27519
        name = func.name.lower()
        if name == "sum":
            if not func.unique:
                return gp.sum(min_count=1), True
            else:
                return (
                    gp.apply(
                        lambda x: x.drop_duplicates().sum(min_count=1),
                        meta=pandas.Series(dtype=dtype, index=index),
                    ),
                    False,
                )
        if name in ["avg", "mean"]:
            if not func.unique:
                return gp.mean(), True
            else:
                return (
                    gp.apply(
                        lambda x: x.drop_duplicates().mean(),
                        meta=pandas.Series(dtype="f8", index=index),
                    ),
                    False,
                )
        if name in ["first", "first_value"]:
            if func.dropna:
                return gp.first(), True
            else:
                # in distributed system, there is no strict order
                # so first or last can be equivalent to choosing any value
                return gp.first(), True
        if name in ["last", "last_value"]:
            if func.dropna:
                return gp.last(), True
            else:
                # in distributed system, there is no strict order
                # so first or last can be equivalent to choosing any value
                return gp.last(), True
        if name == "count":
            if not func.unique and not func.dropna:
                return gp.size(), True
            if func.unique:
                if func.dropna:
                    return gp.nunique(), True
                else:
                    return (
                        gp.apply(
                            lambda x: x.drop_duplicates().size,
                            meta=pandas.Series(dtype="i8", index=index),
                        ),
                        False,
                    )
            if not func.unique and func.dropna:
                return gp.count(), True
        if name == "min":
            if numpy.issubdtype(dtype, numpy.number):
                return gp.min(), True

            def min_(s: Any) -> Any:
                return s.apply(lambda x: x.dropna().min())

            agg = pd.Aggregation("min", min_, min_)
            return gp.agg(agg), True
        if name == "max":
            if numpy.issubdtype(dtype, numpy.number):
                return gp.max(), True

            def max_(s: Any) -> Any:
                return s.apply(lambda x: x.dropna().max())

            agg = pd.Aggregation("max", max_, max_)
            return gp.agg(agg), True
        raise NotImplementedError  # pragma: no cover

    def _count_all(self, df_agg: Any, func: AggFunctionSpec) -> Any:
        assert_or_throw(
            "count" == func.name.lower() and not func.unique,
            ValueError(f"{func} is invalid"),
        )
        return df_agg.size()

    def _count_unique(
        self, df: Any, keys: List[str], cols: str, func: AggFunctionSpec
    ) -> Any:
        assert_or_throw(
            "count" == func.name.lower() and func.unique,
            ValueError(f"{func} can't be applied on {cols}"),
        )
        if cols == "*":
            dkeys = set(df.columns)
        else:
            dkeys = set(keys)
            dkeys.update(cols.split(","))
        return df[list(dkeys)].drop_duplicates().groupby(keys).size()

    def _agg_no_gp(self, func: AggFunctionSpec, x: Any) -> Any:  # noqa: C901
        name = func.name.lower()
        if name == "sum":
            # bug https://github.com/dask/dask/issues/6563
            if not func.unique:
                return x.to_frame().sum(min_count=1).compute()[0]
            else:
                return x.to_frame().drop_duplicates().sum(min_count=1).compute()[0]
        if name in ["avg", "mean"]:
            if not func.unique:
                return x.mean()
            else:
                return x.drop_duplicates().mean()
        if name in ["first", "first_value"]:
            if func.dropna:
                return x.dropna().head(1, compute=False)
            else:
                return x.head(1, compute=False)
        if name in ["last", "last_value"]:
            if func.dropna:
                return x.dropna().tail(1, compute=False)
            else:
                return x.tail(1, compute=False)
        if name == "count":
            if not func.unique and not func.dropna:
                return x.size
            if func.unique and not func.dropna:
                return x.drop_duplicates().size
            if func.unique and func.dropna:
                return x.nunique()
            if not func.unique and func.dropna:
                return x.count()
        if name == "min":
            return x.dropna().min()
        if name == "max":
            return x.dropna().max()
        raise NotImplementedError  # pragma: no cover

    def _count_all_no_group(self, df: Any, func: AggFunctionSpec) -> Any:
        assert_or_throw(
            "count" == func.name.lower() and not func.unique,
            ValueError(f"{func} is invalid"),
        )
        return df.shape[0]

    def _count_unique_no_group(self, df: Any, cols: str, func: AggFunctionSpec) -> Any:
        assert_or_throw(
            "count" == func.name.lower() and func.unique,
            ValueError(f"{func} can't be applied on {cols}"),
        )
        if cols == "*":
            dkeys = set(df.columns)
        else:
            dkeys = set(cols.split(","))
        return df[list(dkeys)].drop_duplicates().shape[0]

    def _safe_groupby(
        self, ndf: Any, keys: List[str]
    ) -> Tuple[Any, List[str], pandas.MultiIndex]:
        nulldf = ndf[keys].isnull()
        gp_keys: List[str] = []
        orig_keys = list(ndf.columns)
        for k in keys:
            ndf[k + "_n"] = nulldf[k]
            ndf[k + "_g"] = ndf[k].fillna(0)
            gp_keys.append(k + "_n")
            gp_keys.append(k + "_g")
        ndf = ndf[orig_keys + gp_keys]
        mi_data = [numpy.ndarray(0, ndf[x].dtype) for x in gp_keys]
        mi = pandas.MultiIndex.from_arrays(mi_data, names=gp_keys)
        return ndf.groupby(gp_keys), gp_keys, mi

    def _safe_pandas_groupby(
        self,
        ndf: pandas.DataFrame,
        keys: List[str],
        keep_extra_keys: bool = False,
        as_index: bool = True,
        sort: bool = True,
    ) -> Tuple[Any, List[str]]:
        if not keep_extra_keys:
            ndf = ndf[ndf.columns]
        nulldf = ndf[keys].isnull()
        gp_keys: List[str] = []
        for k in keys:
            ndf[k + "_n"] = nulldf[k]
            ndf[k + "_g"] = ndf[k].fillna(0)
            gp_keys.append(k + "_n")
            gp_keys.append(k + "_g")
        return ndf.groupby(gp_keys, as_index=as_index, sort=sort), gp_keys

    def _prepare_sort(
        self, ndf: Any, order_by: OrderBySpec
    ) -> Tuple[Any, List[str], List[bool]]:
        if len(order_by.keys) == 0:
            return ndf, [], []
        okeys: List[str] = []
        asc: List[bool] = []
        for oi in order_by:
            nk = oi.name + "_null"
            ndf[nk] = ndf[oi.name].isnull()
            okeys.append(nk)
            asc.append(oi.pd_na_position != "first")
            okeys.append(oi.name)
            asc.append(oi.asc)
        return ndf, okeys, asc
