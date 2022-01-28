from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.custom_entities_list import CustomEntitiesList
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    custom_entity_ids: str,
) -> Dict[str, Any]:
    url = "{}/custom-entities:bulk-get".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {
        "customEntityIds": custom_entity_ids,
    }

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[CustomEntitiesList, BadRequestError]]:
    if response.status_code == 200:
        response_200 = CustomEntitiesList.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[CustomEntitiesList, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    custom_entity_ids: str,
) -> Response[Union[CustomEntitiesList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        custom_entity_ids=custom_entity_ids,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    custom_entity_ids: str,
) -> Optional[Union[CustomEntitiesList, BadRequestError]]:
    """ Bulk get custom entities by ID """

    return sync_detailed(
        client=client,
        custom_entity_ids=custom_entity_ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    custom_entity_ids: str,
) -> Response[Union[CustomEntitiesList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        custom_entity_ids=custom_entity_ids,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    custom_entity_ids: str,
) -> Optional[Union[CustomEntitiesList, BadRequestError]]:
    """ Bulk get custom entities by ID """

    return (
        await asyncio_detailed(
            client=client,
            custom_entity_ids=custom_entity_ids,
        )
    ).parsed
