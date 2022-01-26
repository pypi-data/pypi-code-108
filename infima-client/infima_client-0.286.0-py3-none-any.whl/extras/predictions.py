from typing import TYPE_CHECKING, List, Optional

import pandas as pd

from infima_client.core.types import Unset

if TYPE_CHECKING:
    from infima_client.client import InfimaClient

from .utils import (
    DateT,
    frame_chunker,
    handle_date,
    handle_factor_date_range,
    response_to_frame,
)


@frame_chunker("symbols")
def get_as_of_predictions(
    *,
    client: "InfimaClient",
    symbols: List[str],
    as_of: Optional[DateT] = None,
    col: Optional[str] = "cpr",
    wide: bool = True,
) -> Optional[pd.DataFrame]:
    resp = client.api.prediction_v1.get(
        symbols=symbols,
        as_of=handle_date(as_of) if as_of is not None else None,
    )

    if isinstance(resp.predictions, Unset):
        return None
    else:
        path = "predictions->symbol(*)->asOf,values"
        index_cols = ["as_of", "symbol", "factor_date"]
        wide_on = "factor_date" if wide else None
        explode = ["distribution"]
        return response_to_frame(
            resp, path, index_cols, explode=explode, col=col, wide_on=wide_on
        )


@frame_chunker("symbols")
def get_n_months_ahead_predictions(
    *,
    client: "InfimaClient",
    symbols: List[str],
    num_months: int,
    start: Optional[DateT] = None,
    end: Optional[DateT] = None,
    col: Optional[str] = "cpr",
    wide: bool = True,
) -> Optional[pd.DataFrame]:
    resp = client.api.prediction_v1.get_n_months_ahead(
        symbols=symbols,
        num_months=num_months,
        factor_date_range=handle_factor_date_range(start, end),
    )

    if isinstance(resp.predictions, Unset):
        return None
    else:
        path = "predictions->symbol(*)->values"
        index_cols = ["symbol", "factor_date"]
        wide_on = "factor_date" if wide else None
        explode = ["distribution"]
        return response_to_frame(
            resp, path, index_cols, explode=explode, col=col, wide_on=wide_on
        )
