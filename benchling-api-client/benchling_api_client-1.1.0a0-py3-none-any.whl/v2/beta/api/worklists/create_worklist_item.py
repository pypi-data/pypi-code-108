from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.worklist_item import WorklistItem
from ...models.worklist_item_create import WorklistItemCreate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    worklist_id: str,
    json_body: WorklistItemCreate,
) -> Dict[str, Any]:
    url = "{}/worklists/{worklist_id}/items".format(client.base_url, worklist_id=worklist_id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[WorklistItem, WorklistItem, BadRequestError]]:
    if response.status_code == 200:
        response_200 = WorklistItem.from_dict(response.json())

        return response_200
    if response.status_code == 201:
        response_201 = WorklistItem.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[WorklistItem, WorklistItem, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    worklist_id: str,
    json_body: WorklistItemCreate,
) -> Response[Union[WorklistItem, WorklistItem, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        worklist_id=worklist_id,
        json_body=json_body,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    worklist_id: str,
    json_body: WorklistItemCreate,
) -> Optional[Union[WorklistItem, WorklistItem, BadRequestError]]:
    """Appends an item to the end of a worklist if the item is not already present in the worklist. Returns 200 OK if the item was already present in the worklist and does not change that item's position."""

    return sync_detailed(
        client=client,
        worklist_id=worklist_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    worklist_id: str,
    json_body: WorklistItemCreate,
) -> Response[Union[WorklistItem, WorklistItem, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        worklist_id=worklist_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    worklist_id: str,
    json_body: WorklistItemCreate,
) -> Optional[Union[WorklistItem, WorklistItem, BadRequestError]]:
    """Appends an item to the end of a worklist if the item is not already present in the worklist. Returns 200 OK if the item was already present in the worklist and does not change that item's position."""

    return (
        await asyncio_detailed(
            client=client,
            worklist_id=worklist_id,
            json_body=json_body,
        )
    ).parsed
