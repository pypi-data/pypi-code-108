from typing import Any, Callable, Dict, List, Tuple, Union

import modin.pandas as pd
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


def run_sql_on_ray(
    sql: str, dfs: Dict[str, Any], ignore_case: bool = False
) -> pd.DataFrame:
    return run_sql(QPDRayEngine(), sql, dfs, ignore_case=ignore_case)


class RayUtils(PandasLikeUtils[pd.DataFrame, pd.Series]):
    def drop_duplicates(self, ndf: pd.DataFrame) -> pd.DataFrame:
        # overwrite due to bug
        # https://github.com/modin-project/modin/issues/1959
        keys = list(ndf.columns)
        if ndf.empty:
            return ndf
        if not isinstance(ndf.index, pd.RangeIndex):
            ndf = ndf.reset_index(drop=True)
        nulldf = ndf[keys].isnull().rename({x: x + "_ddn" for x in keys})
        filled = ndf[keys].fillna(0).rename({x: x + "_ddg" for x in keys})
        tp = pd.concat([filled, nulldf], axis=1).apply(tuple, axis=1)
        tp = tp.drop_duplicates().isnull().rename("__dedup__")
        ndf = ndf.merge(tp, how="inner", left_index=True, right_index=True)
        return ndf[keys]


class QPDRayEngine(QPDEngine):
    @property
    def pl_utils(self) -> RayUtils:
        return RayUtils()

    def to_df(self, obj: Any) -> DataFrame:
        if isinstance(obj, DataFrame):
            return obj
        if isinstance(obj, pandas.DataFrame):
            df = pd.DataFrame(obj)
            return DataFrame(Column(df[x], x) for x in df.columns.tolist())
        if isinstance(obj, pd.DataFrame):
            return DataFrame(Column(obj[x], x) for x in obj.columns.tolist())
        raise ValueError(f"{obj} is not supported")  # pragma: no cover

    def to_col(self, value: Any, name: str = "") -> Column:
        if isinstance(value, list):
            pdf = pandas.DataFrame({name: value})
            ddf = pd.DataFrame(pdf)
            return Column(ddf[name], name)
        return Column(value, name)

    def to_native(self, df: DataFrame) -> Any:
        if all(not self.is_series(x.native) for x in df.values()):
            return pd.DataFrame({k: [v.native] for k, v in df.items()})
        values = {k: v.native for k, v in df.items() if not self.is_series(v.native)}
        series = [v.native.rename(k) for k, v in df.items() if self.is_series(v.native)]
        assert_or_throw(
            len(series) > 0, ValueError("DataFrame doesn't contain any series")
        )
        ddf = series[0].to_frame()
        if ddf.empty:
            assert_or_throw(
                len(values) == 0, ValueError("series are empty but values are not")
            )
            res = pd.DataFrame([], columns=[s.name for s in series])
            return res.astype({s.name: s.dtype for s in series})
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
        if len(order_by) == 0 and limit < 0:  # pragma: no cover
            return df
        ndf = self.to_native(df)
        if len(order_by) == 0 or limit == 0:
            return self.to_df(ndf.head(limit))

        # as of modin 0.8.0, the following will all run on driver
        # it can be very expensive
        ndf, sort_keys, asc = self._prepare_sort(ndf, order_by)
        ndf = ndf.sort_values(sort_keys, ascending=asc).head(limit)
        return self.to_df(ndf[list(df.keys())])

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
            ValueError("for ray engine, order by requires partition by"),
        )
        assert_or_throw(
            func.has_partition_by,
            ValueError("for ray engine, partition by is required for row_number()"),
        )
        keys = list(df.keys())
        ndf = self.to_native(df)
        ndf, sort_keys, asc = self._prepare_sort(ndf, func.window.order_by)
        gp = self._safe_groupby(ndf, func.window.partition_keys)
        if not func.has_order_by:  # pragma: no cover
            # unable to have deterministic test
            col = gp.get(None, False, False).cumcount() + 1
            ndf[dest_col_name] = col
            return self.to_df(ndf[keys + [dest_col_name]])

        def gp_apply(df: Any) -> Any:
            df = df.sort_values(sort_keys, ascending=asc)
            col = numpy.arange(1, 1 + df.shape[0])
            df[dest_col_name] = col
            return df.reset_index(drop=True)

        meta = [(ndf[x].name, ndf[x].dtype) for x in ndf.columns]
        meta += [(dest_col_name, "int64")]

        ndf = gp.get(None, False, False).apply(gp_apply).reset_index(drop=True)
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
            ValueError("for ray engine, order by requires partition by"),
        )
        assert_or_throw(
            func.has_partition_by,
            ValueError("for ray engine, partition by is required for ranking"),
        )
        ndf = self.to_native(df)
        keys = list(df.keys())
        ndf, sort_keys, asc = self._prepare_sort(ndf, func.window.order_by)
        gp = self._safe_groupby(ndf, func.window.partition_keys)

        def gp_apply(gdf: Any) -> Any:
            gdf = gdf.sort_values(sort_keys, ascending=asc)
            rank_on = self._safe_pandas_groupby(
                gdf, sort_keys, as_index=False, sort=False
            )[0].ngroup()
            gdf[dest_col_name] = rank_func(rank_on)
            return gdf.reset_index(drop=True)

        meta = [(ndf[x].name, ndf[x].dtype) for x in ndf.columns]
        meta += [(dest_col_name, "f8")]

        ndf = gp.get(None, False, False).apply(gp_apply).reset_index(drop=True)
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
            ValueError("for ray engine, order by requires partition by"),
        )
        assert_or_throw(
            func.has_partition_by,
            ValueError("for ray engine, partition by is required for lead/lag"),
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
        gp = self._safe_groupby(ndf, func.window.partition_keys)

        def gp_apply(gdf: Any) -> Any:
            gdf = gdf.sort_values(sort_keys, ascending=asc)
            gdf[dest_col_name] = l_func(gdf[[col]], delta, default)[col]
            return gdf.reset_index(drop=True)

        meta = [(ndf[x].name, ndf[x].dtype) for x in ndf.columns]
        meta += [(dest_col_name, ndf[col].dtype)]

        ndf = gp.get(None, False, False).apply(gp_apply).reset_index(drop=True)
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
            ValueError("for ray engine, order by requires partition by"),
        )
        assert_or_throw(
            func.has_partition_by,
            ValueError(
                "for ray engine, partition by is required for window aggregation"
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
        gp = self._safe_groupby(ndf, func.window.partition_keys)

        def gp_apply(gdf: Any) -> Any:
            if len(sort_keys) > 0:
                gdf = gdf.sort_values(sort_keys, ascending=asc)
            if not func.has_windowframe:
                res: Any = agg_func(gdf[[col]])[col]
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

        ndf = gp.get(None, False, False).apply(gp_apply).reset_index(drop=True)
        return self.to_df(ndf[keys + [dest_col_name]])

    def _group_agg_with_keys(  # noqa: C901
        self,
        df: DataFrame,
        keys: List[str],
        agg_map: Dict[str, Tuple[str, AggFunctionSpec]],
    ) -> DataFrame:
        ndf = self.to_native(df)
        ndf["__dummy__"] = 1
        gp = self._safe_groupby(ndf, keys)
        # we need dummy to make sure each group is present in the result
        dummy = gp.get("__dummy__", False, False).min()["__dummy__"]
        col_group1: List[pd.Series] = [dummy]
        for k, v in agg_map.items():
            if "*" in v[0] or "," in v[0]:
                continue
            series = self._agg_gp(v[0], v[1], gp)
            series = series.rename(k)
            col_group1.append(series)
        for k, v in agg_map.items():
            if "*" in v[0] or "," in v[0]:
                if v[1].unique:
                    series = self._count_unique(gp, v[0], v[1]).rename(k)
                    col_group1.append(series)
                else:
                    series = self._count_all(gp, v[1]).rename(k)
                    col_group1.append(series)
        assert_or_throw(len(col_group1) > 0, ValueError("No aggregation happened"))
        res = col_group1[0].to_frame()
        for s in col_group1[1:]:
            res[s.name] = s
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
        res = pd.DataFrame({k: [v] for k, v in aggs.items()})
        return self.to_df(res)

    def _agg_gp(  # noqa: C901
        self, key: str, func: AggFunctionSpec, gp: "_LazyGrouper"
    ) -> Any:
        # TODO: this function has compatibility issue with pandas < 1
        # for example: we want to compute the sum of a same column twice
        # https://github.com/pandas-dev/pandas/issues/27519
        name = func.name.lower()
        dtype = gp.dtypes[key]
        if name == "sum":
            return gp.get(key, func.unique, True).sum()[key]
        if name in ["avg", "mean"]:
            return gp.get(key, func.unique, True).mean()[key]
        if name in ["first", "first_value"]:
            return gp.get(key, False, False).first()[key]
        if name in ["last", "last_value"]:
            return gp.get(key, False, False).last()[key]
        if name == "count":
            if not func.unique and not func.dropna:
                return gp.get(key, False, False).size()
            if func.unique:
                if func.dropna:
                    return gp.get(key, False, False).nunique()[key]
                else:
                    return gp.get(key, True, False).size()
            if not func.unique and func.dropna:
                return gp.get(key, False, False).count()[key]
        if name == "min":
            if numpy.issubdtype(dtype, numpy.number):
                return gp.get(key, False, False).min()[key]
            return gp.get(key, False, True).min()[key]
        if name == "max":
            if numpy.issubdtype(dtype, numpy.number):
                return gp.get(key, False, False).max()[key]
            return gp.get(key, False, True).max()[key]
        raise NotImplementedError  # pragma: no cover

    def _count_all(self, gp: "_LazyGrouper", func: AggFunctionSpec) -> Any:
        assert_or_throw(
            "count" == func.name.lower() and not func.unique,
            ValueError(f"{func} is invalid"),
        )
        return gp.get(None, False, False).size()

    def _count_unique(
        self, gp: "_LazyGrouper", cols: str, func: AggFunctionSpec
    ) -> Any:
        assert_or_throw(
            "count" == func.name.lower() and func.unique,
            ValueError(f"{func} can't be applied on {cols}"),
        )
        if cols == "*":
            dkeys: Any = None
        else:
            dkeys = cols.split(",")
        return gp.get(dkeys, True, False).size()

    def _agg_no_gp(self, func: AggFunctionSpec, x: Any) -> Any:  # noqa: C901
        name = func.name.lower()
        if name == "sum":
            if not func.unique:
                return x.sum(min_count=1)
            else:
                return x.drop_duplicates().sum(min_count=1)
        if name in ["avg", "mean"]:
            if func.unique:
                x = x.drop_duplicates()
            if pandas.__version__ >= "1.1":
                # for unclear reason, ray has issue on mean for pandas>=1.1
                ct = x.count()
                if ct == 0:
                    return float("nan")
                sm = x.sum()
                return sm / ct
            return x.mean()
        if name in ["first", "first_value"]:
            if func.dropna:
                return x[x.first_valid_index()]
            else:
                return x.head(1).values.tolist()[0]
        if name in ["last", "last_value"]:
            if func.dropna:
                return x[x.last_valid_index()]
            else:
                return x.tail(1).values.tolist()[0]
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

    def _safe_groupby(self, ndf: Any, keys: List[str]) -> "_LazyGrouper":
        nulldf = ndf[keys].isnull()
        filled = ndf[keys].fillna(0)
        gp_keys1: List[str] = []
        gp_keys2: List[str] = []
        orig_keys = list(ndf.columns)
        for k in keys:
            ndf[k + "_g"] = filled[k]
            ndf[k + "_n"] = nulldf[k]
            gp_keys1.append(k + "_g")
            gp_keys2.append(k + "_n")
        # the following 2 lines are to deal with
        # https://github.com/modin-project/modin/issues/1952
        gp_keys = gp_keys2 + gp_keys1
        ndf = ndf[gp_keys1 + gp_keys2 + orig_keys]
        return _LazyGrouper(ndf, gp_keys)

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


class _LazyGrouper(RayUtils):
    def __init__(self, ndf: Any, gp_keys: List[str]):
        self.ndf = ndf
        self.gp_keys = gp_keys
        mi_data = [numpy.ndarray(0, ndf[x].dtype) for x in gp_keys]
        self.index = pandas.MultiIndex.from_arrays(mi_data, names=gp_keys)
        self.dtypes = {x: ndf[x].dtype for x in ndf.columns}

    def get(self, key: Union[None, str, List[str]], unique: bool, dropna: bool) -> Any:
        ndf = self.ndf
        if key is not None:
            if isinstance(key, str):
                ndf = self.ndf[self.gp_keys + [key]]
            else:
                ndf = self.ndf[self.gp_keys + key]
        if dropna:
            ndf = ndf.dropna(subset=[key])
        if unique:
            ndf = self.drop_duplicates(ndf)
        return ndf.groupby(self.gp_keys)
