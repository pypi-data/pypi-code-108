from typing import Any, Dict

import httpx

from ...client import Client
from ...types import UNSET, Response


def _get_kwargs(
    *,
    client: Client,
    id: int,
    name: str,
) -> Dict[str, Any]:
    url = "{}/pipelines/{id}/name".format(client.base_url, id=id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "name": name,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _build_response(*, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=None,
    )


def sync_detailed(
    *,
    client: Client,
    id: int,
    name: str,
) -> Response[Any]:
    kwargs = _get_kwargs(
        client=client,
        id=id,
        name=name,
    )

    response = httpx.put(
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    *,
    client: Client,
    id: int,
    name: str,
) -> Response[Any]:
    kwargs = _get_kwargs(
        client=client,
        id=id,
        name=name,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.put(**kwargs)

    return _build_response(response=response)
