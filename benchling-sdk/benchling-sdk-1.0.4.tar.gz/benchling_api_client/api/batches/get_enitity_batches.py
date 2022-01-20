from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.batches_paginated_list import BatchesPaginatedList
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    entity_id: str,
) -> Dict[str, Any]:
    url = "{}/entities/{entity_id}/batches".format(client.base_url, entity_id=entity_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[BatchesPaginatedList, BadRequestError]]:
    if response.status_code == 200:
        response_200 = BatchesPaginatedList.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[BatchesPaginatedList, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    entity_id: str,
) -> Response[Union[BatchesPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        entity_id=entity_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    entity_id: str,
) -> Optional[Union[BatchesPaginatedList, BadRequestError]]:
    """ Get an entity's batches """

    return sync_detailed(
        client=client,
        entity_id=entity_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    entity_id: str,
) -> Response[Union[BatchesPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        entity_id=entity_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    entity_id: str,
) -> Optional[Union[BatchesPaginatedList, BadRequestError]]:
    """ Get an entity's batches """

    return (
        await asyncio_detailed(
            client=client,
            entity_id=entity_id,
        )
    ).parsed
