from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.concept import Concept
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: str,
    *,
    client: Client,
    lang: Union[Unset, None, str] = "en",
) -> Dict[str, Any]:
    url = "{}/kb/concept/{id}".format(client.base_url, id=id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "lang": lang,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, Concept]]:
    if response.status_code == 200:
        response_200 = Concept.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = response.json()

        return response_400
    if response.status_code == 404:
        response_404 = response.json()

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, Concept]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: Client,
    lang: Union[Unset, None, str] = "en",
) -> Response[Union[Any, Concept]]:
    kwargs = _get_kwargs(
        id=id,
        client=client,
        lang=lang,
    )

    response = httpx.get(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    id: str,
    *,
    client: Client,
    lang: Union[Unset, None, str] = "en",
) -> Optional[Union[Any, Concept]]:
    """ """

    return sync_detailed(
        id=id,
        client=client,
        lang=lang,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: Client,
    lang: Union[Unset, None, str] = "en",
) -> Response[Union[Any, Concept]]:
    kwargs = _get_kwargs(
        id=id,
        client=client,
        lang=lang,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    id: str,
    *,
    client: Client,
    lang: Union[Unset, None, str] = "en",
) -> Optional[Union[Any, Concept]]:
    """ """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            lang=lang,
        )
    ).parsed
