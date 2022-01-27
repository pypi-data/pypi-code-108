from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.new_api_key import NewApiKey
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/apiKeys/".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[NewApiKey]:
    if response.status_code == 200:
        response_200 = NewApiKey.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[NewApiKey]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
) -> Response[NewApiKey]:
    kwargs = _get_kwargs(
        client=client,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
) -> Optional[NewApiKey]:
    """Use this to authenticate when making API calls. Set the value of the `X-ApiKey` header to
    `keyId:keySecret`

    **WARNING:** Generating a new key will invalidate all existing keys.

    The API Key will only be provided once, and cannot be retrieved again later.
    The unhashed keySecret will never be stored in the database.
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
) -> Response[NewApiKey]:
    kwargs = _get_kwargs(
        client=client,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
) -> Optional[NewApiKey]:
    """Use this to authenticate when making API calls. Set the value of the `X-ApiKey` header to
    `keyId:keySecret`

    **WARNING:** Generating a new key will invalidate all existing keys.

    The API Key will only be provided once, and cannot be retrieved again later.
    The unhashed keySecret will never be stored in the database.
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
