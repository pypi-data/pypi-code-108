from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.location import Location
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    location_id: str,
) -> Dict[str, Any]:
    url = "{}/locations/{location_id}".format(client.base_url, location_id=location_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Location, None, NotFoundError]]:
    if response.status_code == 200:
        response_200 = Location.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = None

        return response_400
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Location, None, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    location_id: str,
) -> Response[Union[Location, None, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        location_id=location_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    location_id: str,
) -> Optional[Union[Location, None, NotFoundError]]:
    """ Get a location by ID """

    return sync_detailed(
        client=client,
        location_id=location_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    location_id: str,
) -> Response[Union[Location, None, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        location_id=location_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    location_id: str,
) -> Optional[Union[Location, None, NotFoundError]]:
    """ Get a location by ID """

    return (
        await asyncio_detailed(
            client=client,
            location_id=location_id,
        )
    ).parsed
