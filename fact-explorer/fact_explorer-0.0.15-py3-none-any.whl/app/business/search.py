from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from fact_explorer.app.business.crypto_helpers import decrypt_result
from fact_explorer.app.db.db_session import Database


async def strict(
    *,
    db: Database,
    skip: int = 0,
    limit: int = 20,
    hq: Optional[Dict[str, Any]] = None,
    pq: Optional[Dict[str, Any]] = None,
    decrypt: bool = False,
) -> List[Dict[str, Any]]:

    if hq is None:
        hq = {}
    if pq is None:
        pq = {}

    response = await db.fetch_by_example(
        offset=skip, limit=limit, header_example=hq, payload_example=pq
    )
    if decrypt:
        result = await decrypt_result(data=response)
    else:
        result = response
    return result


async def time_interval(
    *,
    db: Database,
    start: Optional[datetime] = None,
    minutes: int = 15,
    decrypt: bool = False,
) -> List[Dict[str, Any]]:
    if not start:
        start = datetime.now()
    minutes_ago = start - timedelta(minutes=minutes)
    response = await db.fetch_by_time(until=minutes_ago)

    if decrypt:
        result = await decrypt_result(data=response)
    else:
        result = response
    return result
