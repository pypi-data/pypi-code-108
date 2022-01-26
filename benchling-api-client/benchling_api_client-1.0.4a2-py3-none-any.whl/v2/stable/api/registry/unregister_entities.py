from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.empty_object import EmptyObject
from ...models.unregister_entities import UnregisterEntities
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    registry_id: str,
    json_body: UnregisterEntities,
) -> Dict[str, Any]:
    url = "{}/registries/{registry_id}:unregister-entities".format(client.base_url, registry_id=registry_id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[EmptyObject, BadRequestError]]:
    if response.status_code == 200:
        response_200 = EmptyObject.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[EmptyObject, BadRequestError]]:
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
    json_body: UnregisterEntities,
) -> Response[Union[EmptyObject, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        registry_id=registry_id,
        json_body=json_body,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    registry_id: str,
    json_body: UnregisterEntities,
) -> Optional[Union[EmptyObject, BadRequestError]]:
    """ Unregisters entities and moves them to a folder """

    return sync_detailed(
        client=client,
        registry_id=registry_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    registry_id: str,
    json_body: UnregisterEntities,
) -> Response[Union[EmptyObject, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        registry_id=registry_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    registry_id: str,
    json_body: UnregisterEntities,
) -> Optional[Union[EmptyObject, BadRequestError]]:
    """ Unregisters entities and moves them to a folder """

    return (
        await asyncio_detailed(
            client=client,
            registry_id=registry_id,
            json_body=json_body,
        )
    ).parsed
