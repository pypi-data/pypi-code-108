import httpx

from impressive_strawberry.database import tables
from impressive_strawberry.web.models import full


async def notify_unlock(url: str, unlock: tables.Unlock) -> None:
    # Serialize the unlock with Pydantic
    serialized = full.UnlockFull.from_orm(unlock)
    # Send the post request
    async with httpx.AsyncClient() as client:
        response: httpx.Response = await client.post(url, json=serialized.dict())
        # Raise if the request fails
        response.raise_for_status()
