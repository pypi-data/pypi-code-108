from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.mixture import Mixture
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    mixture_id: str,
) -> Dict[str, Any]:
    url = "{}/mixtures/{mixture_id}".format(client.base_url, mixture_id=mixture_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Mixture, BadRequestError]]:
    if response.status_code == 200:
        response_200 = Mixture.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Mixture, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    mixture_id: str,
) -> Response[Union[Mixture, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        mixture_id=mixture_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    mixture_id: str,
) -> Optional[Union[Mixture, BadRequestError]]:
    """ Get a mixture """

    return sync_detailed(
        client=client,
        mixture_id=mixture_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    mixture_id: str,
) -> Response[Union[Mixture, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        mixture_id=mixture_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    mixture_id: str,
) -> Optional[Union[Mixture, BadRequestError]]:
    """ Get a mixture """

    return (
        await asyncio_detailed(
            client=client,
            mixture_id=mixture_id,
        )
    ).parsed
