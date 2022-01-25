from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.container import Container
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    container_id: str,
) -> Dict[str, Any]:
    url = "{}/containers/{container_id}".format(client.base_url, container_id=container_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
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
) -> Response[Union[Container, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        container_id=container_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    container_id: str,
) -> Optional[Union[Container, BadRequestError, NotFoundError]]:
    """ get a container by id """

    return sync_detailed(
        client=client,
        container_id=container_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    container_id: str,
) -> Response[Union[Container, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        container_id=container_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    container_id: str,
) -> Optional[Union[Container, BadRequestError, NotFoundError]]:
    """ get a container by id """

    return (
        await asyncio_detailed(
            client=client,
            container_id=container_id,
        )
    ).parsed
