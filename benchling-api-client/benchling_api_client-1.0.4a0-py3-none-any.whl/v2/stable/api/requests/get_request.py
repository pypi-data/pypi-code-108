from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.not_found_error import NotFoundError
from ...models.request import Request
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    request_id: str,
) -> Dict[str, Any]:
    url = "{}/requests/{request_id}".format(client.base_url, request_id=request_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Request, NotFoundError]]:
    if response.status_code == 200:
        response_200 = Request.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Request, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    request_id: str,
) -> Response[Union[Request, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        request_id=request_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    request_id: str,
) -> Optional[Union[Request, NotFoundError]]:
    """ Get a request by ID """

    return sync_detailed(
        client=client,
        request_id=request_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    request_id: str,
) -> Response[Union[Request, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        request_id=request_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    request_id: str,
) -> Optional[Union[Request, NotFoundError]]:
    """ Get a request by ID """

    return (
        await asyncio_detailed(
            client=client,
            request_id=request_id,
        )
    ).parsed
