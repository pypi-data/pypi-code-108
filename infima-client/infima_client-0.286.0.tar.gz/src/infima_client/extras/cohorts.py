from typing import TYPE_CHECKING, Dict, List, Optional

from infima_client.core.types import Unset

from .utils import DateT, frame_chunker, handle_factor_date

if TYPE_CHECKING:
    from infima_client.client import InfimaClient


def get_member_lists(
    *, client: "InfimaClient", cohorts: List[str], factor_date: Optional[DateT] = None
) -> Optional[Dict[str, List[str]]]:
    resp = client.api.cohort_v1.get_member_lists(
        cohorts=cohorts,
        factor_date=handle_factor_date(factor_date)
        if factor_date is not None
        else None,
    )
    if isinstance(resp.member_lists, Unset):
        return None

    out: Dict[str, List[str]] = {}
    for key in resp.member_lists.additional_keys:
        cusips = resp.member_lists[key].cusips
        if isinstance(cusips, Unset):
            continue
        out[key] = cusips

    return out
