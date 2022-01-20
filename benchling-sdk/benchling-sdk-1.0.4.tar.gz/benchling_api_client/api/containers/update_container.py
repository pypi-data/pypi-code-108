from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.container import Container
from ...models.container_update import ContainerUpdate
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    container_id: str,
    json_body: ContainerUpdate,
) -> Dict[str, Any]:
    url = "{}/containers/{container_id}".format(client.base_url, container_id=container_id)

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
) -> Optional[Union[Container, BadRequestError, NotFoundError]]:
    if response.status_code == 200:
        response_200 = Container.from_dict(response.json())

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
) -> Response[Union[Container, BadRequestError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    container_id: str,
    json_body: ContainerUpdate,
) -> Response[Union[Container, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        container_id=container_id,
        json_body=json_body,
    )

    response = httpx.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    container_id: str,
    json_body: ContainerUpdate,
) -> Optional[Union[Container, BadRequestError, NotFoundError]]:
    """ update a container """

    return sync_detailed(
        client=client,
        container_id=container_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    container_id: str,
    json_body: ContainerUpdate,
) -> Response[Union[Container, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        container_id=container_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    container_id: str,
    json_body: ContainerUpdate,
) -> Optional[Union[Container, BadRequestError, NotFoundError]]:
    """ update a container """

    return (
        await asyncio_detailed(
            client=client,
            container_id=container_id,
            json_body=json_body,
        )
    ).parsed
