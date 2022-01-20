from typing import Any, Dict, List, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.not_found_error import NotFoundError
from ...models.registered_entities_list import RegisteredEntitiesList
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    registry_id: str,
    entity_registry_ids: List[str],
) -> Dict[str, Any]:
    url = "{}/registries/{registry_id}/registered-entities:bulk-get".format(
        client.base_url, registry_id=registry_id
    )

    headers: Dict[str, Any] = client.get_headers()

    json_entity_registry_ids = entity_registry_ids

    params: Dict[str, Any] = {
        "entityRegistryIds": json_entity_registry_ids,
    }

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[RegisteredEntitiesList, BadRequestError, NotFoundError]]:
    if response.status_code == 200:
        response_200 = RegisteredEntitiesList.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[RegisteredEntitiesList, BadRequestError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    registry_id: str,
    entity_registry_ids: List[str],
) -> Response[Union[RegisteredEntitiesList, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        registry_id=registry_id,
        entity_registry_ids=entity_registry_ids,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    registry_id: str,
    entity_registry_ids: List[str],
) -> Optional[Union[RegisteredEntitiesList, BadRequestError, NotFoundError]]:
    """ Bulk get registered entities """

    return sync_detailed(
        client=client,
        registry_id=registry_id,
        entity_registry_ids=entity_registry_ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    registry_id: str,
    entity_registry_ids: List[str],
) -> Response[Union[RegisteredEntitiesList, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        registry_id=registry_id,
        entity_registry_ids=entity_registry_ids,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    registry_id: str,
    entity_registry_ids: List[str],
) -> Optional[Union[RegisteredEntitiesList, BadRequestError, NotFoundError]]:
    """ Bulk get registered entities """

    return (
        await asyncio_detailed(
            client=client,
            registry_id=registry_id,
            entity_registry_ids=entity_registry_ids,
        )
    ).parsed
