from typing import Any, Dict, List
from fastapi import APIRouter, Request, HTTPException
import pyjson5 as json5
from fact_explorer.app.api.constants import API_RESPONSES

from fact_explorer.app.business import search
from fact_explorer.app.business.crypto_helpers import cryptoshred_enabled
from fact_explorer.app.business.registry import schema_registry_enabled
from fact_explorer.app.entities.fact import FactOut
from fact_explorer.config import get_logger

log = get_logger("api.router")

router = APIRouter(
    prefix="/api",
    responses=API_RESPONSES,
)


@router.get("/search", response_model=List[FactOut])
async def root(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    hq: str = "{}",
    pq: str = "{}",
    decrypt: bool = False,
) -> List[Dict[str, Any]]:
    """
    Query the Facts received. Results are ordered by when the where received.
    Newest first.

    - `skip`: skip the X newest entries
    - `limit`: display X facts
    - `hq`: the header query. Use query by example here
    Just send a dict of what you are looking for.
    - `pq`: the payload query. Use query by example here.
    Just send a dict of what you are looking for.
    - `decrypt`: whether or not to decrypt cryptoshred information
    (Caution might increase response time significantly)
    """
    try:
        header_query = json5.decode(hq)
        payload_query = json5.decode(pq)
    except json5.Json5DecoderException as e:
        log.debug(e)
        raise HTTPException(status_code=400, detail="Invalid JSON5 parameters")

    result = await search.strict(
        db=request.app.state.db,
        skip=skip,
        limit=limit,
        hq=header_query,
        pq=payload_query,
        decrypt=decrypt,
    )
    return result


@router.get("/last", response_model=List[FactOut])
async def last(
    request: Request, minutes: int = 15, decrypt: bool = False
) -> List[Dict[str, Any]]:
    """
    Displays the Facts received in the last X minutes. Results are ordered,
    newest first.

    Beware that this is a very expensive operations in terms of memory and time.
    Use with care, you will kill the application if you use to large values.

    - `minutes`: How many minutes from now backwards you want to get.
    - `decrypt`: whether or not to decrypt cryptoshred information
    (Caution might increase response time significantly)
    """
    result = await search.time_interval(
        db=request.app.state.db,
        minutes=minutes,
        decrypt=decrypt,
    )
    return result


@router.get("/features")
async def features() -> Dict[str, bool]:
    """
    Returns an object containing as keys the set of optional features.
    The values indicate if that feature is currently available.
    """
    return {
        "cryptoshred": await cryptoshred_enabled(),
        "schema_registry": await schema_registry_enabled(),
    }
