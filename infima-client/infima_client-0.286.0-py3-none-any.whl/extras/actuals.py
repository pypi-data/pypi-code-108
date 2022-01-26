from typing import TYPE_CHECKING, List, Optional

import pandas as pd

from infima_client.core.types import Unset

from .utils import DateT, frame_chunker, handle_factor_date_range, response_to_frame

if TYPE_CHECKING:
    from infima_client.client import InfimaClient


def _get_pool_actuals(
    *,
    client: "InfimaClient",
    cusips: List[str],
    start: Optional[DateT] = None,
    end: Optional[DateT] = None,
    col: Optional[str] = "cpr",
    wide: bool = True,
) -> Optional[pd.DataFrame]:
    resp = client.api.pool_v1.get_actual_prepayments(
        cusips=cusips, factor_date_range=handle_factor_date_range(start, end)
    )
    if isinstance(resp.prepayments, Unset):
        return None
    else:
        path = "prepayments->symbol(*)->values"
        index_cols = ["symbol", "factor_date"]
        wide_on = "factor_date" if wide else None
        return response_to_frame(resp, path, index_cols, col=col, wide_on=wide_on)


def _get_cohort_actuals(
    *,
    client: "InfimaClient",
    cohorts: List[str],
    start: Optional[DateT] = None,
    end: Optional[DateT] = None,
    col: Optional[str] = "cpr",
    wide: bool = True,
) -> Optional[pd.DataFrame]:
    resp = client.api.cohort_v1.get_actual_prepayments(
        cohorts=cohorts, factor_date_range=handle_factor_date_range(start, end)
    )
    if isinstance(resp.prepayments, Unset):
        return None
    else:
        path = "prepayments->symbol(*)->values"
        index_cols = ["symbol", "factor_date"]
        wide_on = "factor_date" if wide else None
        return response_to_frame(resp, path, index_cols, col=col, wide_on=wide_on)


def _get_actuals(
    *,
    client: "InfimaClient",
    symbols: List[str],
    start: Optional[DateT] = None,
    end: Optional[DateT] = None,
    col: Optional[str] = "cpr",
    wide: bool = True,
) -> Optional[pd.DataFrame]:
    dfs = []
    pool_df = _get_pool_actuals(
        client=client,
        cusips=symbols,
        start=start,
        end=end,
        col=col,
        wide=wide,
    )
    if pool_df is not None and len(pool_df) > 0:
        dfs.append(pool_df)

    cohort_df = _get_cohort_actuals(
        client=client,
        cohorts=symbols,
        start=start,
        end=end,
        col=col,
        wide=wide,
    )
    if cohort_df is not None and len(cohort_df) > 0:
        dfs.append(cohort_df)

    out = pd.concat(dfs)
    return out


get_pool_actuals = frame_chunker("cusips")(_get_pool_actuals)
get_cohort_actuals = frame_chunker("cohorts")(_get_cohort_actuals)
get_actuals = frame_chunker("symbols")(_get_actuals)
