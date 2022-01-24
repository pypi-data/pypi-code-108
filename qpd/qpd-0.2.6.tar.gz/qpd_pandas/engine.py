from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from pandas.api.indexers import BaseIndexer
from qpd import PandasLikeUtils, QPDEngine, run_sql
from qpd.dataframe import Column, DataFrame
from qpd.specs import (
    AggFunctionSpec,
    ArgumentSpec,
    OrderBySpec,
    RollingWindowFrame,
    WindowFunctionSpec,
)
from triad.utils.assertion import assert_or_throw


def run_sql_on_pandas(
    sql: str, dfs: Dict[str, Any], ignore_case: bool = False
) -> pd.DataFrame:
    return run_sql(QPDPandasEngine(), sql, dfs, ignore_case=ignore_case)


class PandasUtils(PandasLikeUtils[pd.DataFrame, pd.Series]):
    pass


class QPDPandasEngine(QPDEngine):
    @property
    def pl_utils(self) -> PandasUtils:
        return PandasUtils()

    def to_df(self, obj: Any) -> DataFrame:
        if isinstance(obj, DataFrame):
            return obj
        if isinstance(obj, pd.DataFrame):
            return DataFrame(Column(v, k) for k, v in obj.to_dict("series").items())
        raise ValueError(f"{obj} is not supported")  # pragma: no cover

    def to_col(self, value: Any, name: str = "") -> Column:
        if isinstance(value, list):
            return Column(pd.Series(value), name)
        return Column(value, name)

    def to_native(self, df: DataFrame) -> Any:
        if all(not self.is_series(x.native) for x in df.values()):
            return pd.DataFrame({k: [v.native] for k, v in df.items()})
        return pd.DataFrame({k: v.native for k, v in df.items()})

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

        def where(pos: int) -> Any:
            return np.where(
                cols[pos].native,
                cols[pos + 1].native,
                cols[pos + 2].native if pos + 3 == len(cols) else where(pos + 2),
            )

        return Column(pd.Series(where(0)))

    def order_by_limit(
        self, df: DataFrame, order_by: OrderBySpec, limit: int
    ) -> DataFrame:
        if len(order_by) == 0 and limit < 0:  # pragma: no cover
            return df
        ndf = self.to_native(df)
        if len(order_by) > 0:
            ndf = self._safe_sort(ndf, order_by)
        if limit >= 0:
            ndf = ndf.head(limit)
        return self.to_df(ndf)

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
                if isinstance(x, pd.Series)
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
        ndf = self.to_native(df)
        ndf = self._safe_sort(ndf, func.window.order_by)
        if func.has_partition_by > 0:
            gp, _ = self._safe_groupby(ndf, func.window.partition_keys)
            col = gp.cumcount() + 1
        else:
            col = np.arange(1, 1 + ndf.shape[0])
        ndf[dest_col_name] = col
        return self.to_df(ndf)

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
        ndf = self.to_native(df)
        ndf = self._safe_sort(ndf, func.window.order_by)
        rank_on = self._safe_groupby(
            ndf, func.window.order_by.keys, as_index=False, sort=False
        )[0].ngroup()
        ndf["_rank_on"] = rank_on
        if len(func.window.partition_keys) > 0:
            gp, _ = self._safe_groupby(ndf, func.window.partition_keys)
            col = rank_func(gp["_rank_on"])
        else:
            col = rank_func(ndf["_rank_on"])
        ndf[dest_col_name] = col
        ndf = ndf[list(df.keys()) + [dest_col_name]]
        return self.to_df(ndf)

    def _window_lead_lag(
        self,
        l_func: Callable,
        df: DataFrame,
        func: WindowFunctionSpec,
        args: List[ArgumentSpec],
        dest_col_name: str,
    ) -> DataFrame:
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
        ndf = self._safe_sort(ndf, func.window.order_by)
        if len(func.window.partition_keys) > 0:
            gp, _ = self._safe_groupby(ndf, func.window.partition_keys)
            col = l_func(gp[col], delta, default)
        else:
            col = l_func(ndf[col], delta, default)
        ndf[dest_col_name] = col
        ndf = ndf[list(df.keys()) + [dest_col_name]]
        return self.to_df(ndf)

    def _window_simple_agg(  # noqa: C901
        self,
        agg_func: Callable,
        df: DataFrame,
        func: WindowFunctionSpec,
        args: List[ArgumentSpec],
        dest_col_name: str,
    ) -> DataFrame:
        assert_or_throw(len(args) == 1 and args[0].is_col, ValueError(f"{args}"))
        assert_or_throw(
            not func.unique and not func.dropna,
            NotImplementedError(
                f"window function doesn't support unique {func.unique} "
                + f"and dropna {func.dropna}"
            ),
        )
        ndf = self.to_native(df)
        ndf = self._safe_sort(ndf, func.window.order_by)
        col = args[0].value
        if not func.has_windowframe:
            if not func.has_partition_by:
                res: Any = agg_func(ndf[col])
            else:
                gp, _ = self._safe_groupby(ndf, func.window.partition_keys)
                res = gp[col].transform(agg_func)
        else:
            wf = func.window.windowframe
            if isinstance(wf, RollingWindowFrame):
                min_p = 0 if func.name in ["count", "min", "max"] else 1
                # 1.1.0 has this bug https://github.com/pandas-dev/pandas/issues/35557
                # we try to use native functions here to bypass bugs
                if wf.start is None and wf.end == 0:
                    rolling_func: Callable = lambda x: x.expanding(min_periods=min_p)
                elif wf.window is not None and wf.end == 0:
                    rolling_func: Callable = lambda x: x.rolling(  # type: ignore
                        window=wf.window, min_periods=min_p
                    )
                else:  # will not work on version pandas 1.1.0
                    rolling_func: Callable = lambda x: x.rolling(  # type: ignore
                        window=_RowsIndexer(wf.start, wf.end), min_periods=min_p
                    )
                if not func.has_partition_by:
                    res = ndf[col]
                    res = agg_func(rolling_func(res))
                else:
                    gp, _ = self._safe_groupby(
                        ndf, func.window.partition_keys, as_index=True
                    )
                    res = agg_func(rolling_func(gp[col]))
                    levels = list(range(len(res.index.names) - 1))
                    if len(levels) > 0:
                        res = res.reset_index(level=levels, drop=True)
            else:  # pragma: no cover
                raise NotImplementedError(wf)
        ndf[dest_col_name] = res
        return self.to_df(ndf)

    def _group_agg_with_keys(
        self,
        df: DataFrame,
        keys: List[str],
        agg_map: Dict[str, Tuple[str, AggFunctionSpec]],
    ) -> DataFrame:
        ndf = self.to_native(df)
        simple_agg_map = {
            k: pd.NamedAgg(column=v[0], aggfunc=self._map_agg_function(v[1]))
            for k, v in agg_map.items()
            if "*" not in v[0] and "," not in v[0]
        }
        gp, gp_keys = self._safe_groupby(ndf, keys, keep_extra_keys=True)
        if len(simple_agg_map) > 0:
            res = gp.agg(**simple_agg_map)
        cts: Dict[str, Any] = {}
        for k, v in agg_map.items():
            if "*" in v[0] or "," in v[0]:
                if v[1].unique:
                    cts[k] = self._count_unique(ndf, gp_keys, v[0], v[1])
                else:
                    cts[k] = self._count_all(gp, v[1])
        if len(simple_agg_map) > 0 and len(cts) == 0:
            return self.to_df(res.reset_index(drop=True))
        if len(simple_agg_map) == 0 and len(cts) > 0:
            return self.to_df(pd.DataFrame(cts).reset_index(drop=True))
        if len(simple_agg_map) > 0 and len(cts) > 0:
            for k, vv in cts.items():
                res[k] = vv
            return self.to_df(res.reset_index(drop=True))
        raise NotImplementedError("Impossible case")  # pragma: no cover

    def _group_agg_no_keys(
        self,
        df: DataFrame,
        agg_map: Dict[str, Tuple[str, AggFunctionSpec]],
    ) -> DataFrame:
        ndf = self.to_native(df)
        simple_agg_map = {
            k: (v[0], self._map_agg_function_no_group(v[1]))
            for k, v in agg_map.items()
            if "*" not in v[0] and "," not in v[0]
        }
        aggs: Dict[str, Any] = {}
        for k, v in simple_agg_map.items():
            aggs[k] = ndf.agg({v[0]: [v[1]]}).iloc[0, 0]
        for k, v in agg_map.items():
            if "*" in v[0] or "," in v[0]:
                if v[1].unique:
                    aggs[k] = self._count_unique_no_group(ndf, v[0], v[1])
                else:
                    aggs[k] = self._count_all_no_group(ndf, v[1])
        res = pd.DataFrame({k: [v] for k, v in aggs.items()})
        return self.to_df(res)

    def _map_agg_function(self, func: AggFunctionSpec) -> Any:  # noqa: C901
        # TODO: this function has compatibility issue with pandas < 1
        # for example: we want to compute the sum of a same column twice
        # https://github.com/pandas-dev/pandas/issues/27519
        name = func.name.lower()
        if name == "sum":
            if not func.unique:
                return lambda x: x.sum(min_count=1)
            else:
                return lambda x: x.drop_duplicates().sum(min_count=1)
        if name in ["avg", "mean"]:
            if not func.unique:
                return "mean"
            else:
                return lambda x: x.drop_duplicates().mean()
        if name in ["first", "first_value"]:
            if func.dropna:
                return "first"
            else:
                return lambda x: x.head(1)
        if name in ["last", "last_value"]:
            if func.dropna:
                return "last"
            else:
                return lambda x: x.tail(1)
        if name == "count":
            if not func.unique and not func.dropna:
                return "size"
            if func.unique:
                return lambda x: x.nunique(dropna=func.dropna)
            if not func.unique and func.dropna:
                return "count"
        if name == "min":
            # probably related with https://github.com/pandas-dev/pandas/issues/31777
            # pandas has to be >=1.0.2
            return lambda x: x.dropna().min()
        if name == "max":
            return lambda x: x.dropna().max()
        return name  # pragma: no cover

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
        return df[dkeys].drop_duplicates().groupby(keys).size()

    def _map_agg_function_no_group(self, func: AggFunctionSpec) -> Any:  # noqa: C901
        name = func.name.lower()
        if name == "sum":
            if not func.unique:
                return lambda x: x.sum(min_count=1)
            else:
                return lambda x: x.drop_duplicates().sum(min_count=1)
        if name in ["avg", "mean"]:
            if not func.unique:
                return "mean"
            else:
                return lambda x: x.drop_duplicates().mean()
        if name in ["first", "first_value"]:
            if func.dropna:
                return lambda x: x[x.first_valid_index()]
            else:
                return lambda x: x.head(1)
        if name in ["last", "last_value"]:
            if func.dropna:
                return lambda x: x[x.last_valid_index()]
            else:
                return lambda x: x.tail(1)
        if name == "count":
            if not func.unique and not func.dropna:
                return "size"
            if func.unique and not func.dropna:
                return lambda x: x.drop_duplicates().size
            if func.unique and func.dropna:
                return "nunique"
            if not func.unique and func.dropna:
                return "count"
        if name == "min":
            return lambda x: x.dropna().min()
        if name == "max":
            return lambda x: x.dropna().max()
        return name  # pragma: no cover

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
        return df[dkeys].drop_duplicates().shape[0]

    def _safe_groupby(
        self,
        ndf: Any,
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

    def _safe_sort(self, ndf: Any, order_by: OrderBySpec) -> Any:
        if len(order_by.keys) == 0:
            return ndf
        keys = list(ndf.columns)
        okeys: List[str] = []
        asc: List[bool] = []
        for oi in order_by:
            nk = oi.name + "_null"
            ndf[nk] = ndf[oi.name].isnull()
            okeys.append(nk)
            asc.append(oi.pd_na_position != "first")
            okeys.append(oi.name)
            asc.append(oi.asc)
        ndf = ndf.sort_values(okeys, ascending=asc)
        return ndf[keys]


class _RowsIndexer(BaseIndexer):
    def __init__(self, start: Optional[int], end: Optional[int], **kwargs: Any):
        window = 0 if start is None or end is None else end - start + 1
        kw = dict(kwargs)
        kw["window_size"] = window
        kw["start"] = start
        kw["end"] = end

        super().__init__(**kw)

    def get_window_bounds(
        self,
        num_values: int = 0,
        min_periods: Optional[int] = None,
        center: Optional[bool] = None,
        closed: Optional[str] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        if self.start is None:
            start = np.zeros(num_values, dtype=np.int64)
        else:
            start = np.arange(self.start, self.start + num_values, dtype=np.int64)
            if self.start < 0:
                start[: -self.start] = 0
            elif self.start > 0:
                start[-self.start :] = num_values
        if self.end is None:
            end = np.full(num_values, num_values, dtype=np.int64)
        else:
            end = np.arange(self.end + 1, self.end + 1 + num_values, dtype=np.int64)
            if self.end > 0:
                end[-self.end :] = num_values
            elif self.end < 0:
                end[: -self.end] = 0
        return start, end
