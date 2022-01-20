from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.dataset import Dataset
from ...types import UNSET, Response


def _get_kwargs(
    *,
    client: Client,
    id: int,
    new_name: str,
) -> Dict[str, Any]:
    url = "{}/datasets/{id}/name".format(client.base_url, id=id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "newName": new_name,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Dataset]:
    if response.status_code == 200:
        response_200 = Dataset.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[Dataset]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    id: int,
    new_name: str,
) -> Response[Dataset]:
    kwargs = _get_kwargs(
        client=client,
        id=id,
        new_name=new_name,
    )

    response = httpx.put(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    id: int,
    new_name: str,
) -> Optional[Dataset]:
    """  """

    return sync_detailed(
        client=client,
        id=id,
        new_name=new_name,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    id: int,
    new_name: str,
) -> Response[Dataset]:
    kwargs = _get_kwargs(
        client=client,
        id=id,
        new_name=new_name,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.put(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    id: int,
    new_name: str,
) -> Optional[Dataset]:
    """  """

    return (
        await asyncio_detailed(
            client=client,
            id=id,
            new_name=new_name,
        )
    ).parsed
