from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.entry import Entry
from ...models.entry_update import EntryUpdate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    entry_id: str,
    json_body: EntryUpdate,
) -> Dict[str, Any]:
    url = "{}/entries/{entry_id}".format(client.base_url, entry_id=entry_id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Entry]:
    if response.status_code == 200:
        response_200 = Entry.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[Entry]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    entry_id: str,
    json_body: EntryUpdate,
) -> Response[Entry]:
    kwargs = _get_kwargs(
        client=client,
        entry_id=entry_id,
        json_body=json_body,
    )

    response = httpx.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    entry_id: str,
    json_body: EntryUpdate,
) -> Optional[Entry]:
    """ Update a notebook entry's metadata """

    return sync_detailed(
        client=client,
        entry_id=entry_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    entry_id: str,
    json_body: EntryUpdate,
) -> Response[Entry]:
    kwargs = _get_kwargs(
        client=client,
        entry_id=entry_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    entry_id: str,
    json_body: EntryUpdate,
) -> Optional[Entry]:
    """ Update a notebook entry's metadata """

    return (
        await asyncio_detailed(
            client=client,
            entry_id=entry_id,
            json_body=json_body,
        )
    ).parsed
