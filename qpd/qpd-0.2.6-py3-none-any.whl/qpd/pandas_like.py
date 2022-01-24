# TODO: This is based on a duplication of Triad PandasLikeUtils
# should we remove PandasLikeUtils from Triad?
from typing import (
    Any,
    Generic,
    List,
    TypeVar,
    Tuple,
)

from triad import assert_or_throw


from triad.utils.pandas_like import PandasLikeUtils as PandasLikeUtilsBase

DfT = TypeVar("DfT", bound=Any)
ColT = TypeVar("ColT", bound=Any)

_ANTI_INDICATOR = "__anti_indicator__"
_CROSS_INDICATOR = "__corss_indicator__"


class PandasLikeUtils(PandasLikeUtilsBase[DfT], Generic[DfT, ColT]):
    """A collection of utils for sql operations on general pandas like dataframes"""

    def parse_join_type(self, join_type: str) -> str:
        join_type = join_type.replace(" ", "").replace("_", "").lower()
        if join_type in ["inner", "cross"]:
            return join_type
        if join_type in ["inner", "join"]:
            return "inner"
        if join_type in ["semi", "leftsemi"]:
            return "left_semi"
        if join_type in ["anti", "leftanti"]:
            return "left_anti"
        if join_type in ["left", "leftouter"]:
            return "left_outer"
        if join_type in ["right", "rightouter"]:
            return "right_outer"
        if join_type in ["outer", "full", "fullouter"]:
            return "full_outer"
        raise NotImplementedError(join_type)

    def drop_duplicates(self, df: DfT) -> DfT:
        return df.drop_duplicates()

    def union(self, ndf1: DfT, ndf2: DfT, unique: bool) -> DfT:
        ndf1, ndf2 = self._preprocess_set_op(ndf1, ndf2)
        ndf = ndf1.append(ndf2)
        if unique:
            ndf = self.drop_duplicates(ndf)
        return ndf

    def intersect(self, df1: DfT, df2: DfT, unique: bool) -> DfT:
        ndf1, ndf2 = self._preprocess_set_op(df1, df2)
        ndf = ndf1.merge(self.drop_duplicates(ndf2))
        if unique:
            ndf = self.drop_duplicates(ndf)
        return ndf

    def except_df(
        self,
        df1: DfT,
        df2: DfT,
        unique: bool,
        anti_indicator_col: str = _ANTI_INDICATOR,
    ) -> DfT:
        ndf1, ndf2 = self._preprocess_set_op(df1, df2)
        # TODO: lack of test to make sure original ndf2 is not changed
        ndf2 = self._with_indicator(ndf2, anti_indicator_col)
        ndf = ndf1.merge(ndf2, how="left", on=list(ndf1.columns))
        ndf = ndf[ndf[anti_indicator_col].isnull()].drop([anti_indicator_col], axis=1)
        if unique:
            ndf = self.drop_duplicates(ndf)
        return ndf

    def join(
        self,
        ndf1: DfT,
        ndf2: DfT,
        join_type: str,
        on: List[str],
        anti_indicator_col: str = _ANTI_INDICATOR,
        cross_indicator_col: str = _CROSS_INDICATOR,
    ) -> DfT:
        join_type = self.parse_join_type(join_type)
        if join_type == "inner":
            ndf1 = ndf1.dropna(subset=on)
            ndf2 = ndf2.dropna(subset=on)
            joined = ndf1.merge(ndf2, how=join_type, on=on)
        elif join_type == "left_semi":
            ndf1 = ndf1.dropna(subset=on)
            ndf2 = self.drop_duplicates(ndf2[on].dropna())
            joined = ndf1.merge(ndf2, how="inner", on=on)
        elif join_type == "left_anti":
            # TODO: lack of test to make sure original ndf2 is not changed
            ndf2 = self.drop_duplicates(ndf2[on].dropna())
            ndf2 = self._with_indicator(ndf2, anti_indicator_col)
            joined = ndf1.merge(ndf2, how="left", on=on)
            joined = joined[joined[anti_indicator_col].isnull()].drop(
                [anti_indicator_col], axis=1
            )
        elif join_type == "left_outer":
            ndf2 = ndf2.dropna(subset=on)
            joined = ndf1.merge(ndf2, how="left", on=on)
        elif join_type == "right_outer":
            ndf1 = ndf1.dropna(subset=on)
            joined = ndf1.merge(ndf2, how="right", on=on)
        elif join_type == "full_outer":
            add: List[str] = []
            for f in on:
                name = f + "_null"
                s1 = ndf1[f].isnull().astype(int)
                ndf1[name] = s1
                s2 = ndf2[f].isnull().astype(int) * 2
                ndf2[name] = s2
                add.append(name)
            joined = ndf1.merge(ndf2, how="outer", on=on + add).drop(add, axis=1)
        elif join_type == "cross":
            assert_or_throw(
                len(on) == 0, ValueError(f"cross join can't have join keys {on}")
            )
            ndf1 = self._with_indicator(ndf1, cross_indicator_col)
            ndf2 = self._with_indicator(ndf2, cross_indicator_col)
            joined = ndf1.merge(ndf2, how="inner", on=[cross_indicator_col]).drop(
                [cross_indicator_col], axis=1
            )
        else:  # pragma: no cover
            raise NotImplementedError(join_type)
        return joined

    def _preprocess_set_op(self, ndf1: DfT, ndf2: DfT) -> Tuple[DfT, DfT]:
        assert_or_throw(
            len(list(ndf1.columns)) == len(list(ndf2.columns)),
            ValueError("two dataframes have different number of columns"),
        )
        ndf2.columns = ndf1.columns  # this is SQL behavior
        return ndf1, ndf2

    def _with_indicator(self, df: DfT, name: str) -> DfT:
        return df.assign(**{name: 1})
