from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.registries_list import RegistriesList
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    name: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/registries".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if not isinstance(name, Unset) and name is not None:
        params["name"] = name
    if not isinstance(modified_at, Unset) and modified_at is not None:
        params["modifiedAt"] = modified_at

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[RegistriesList]:
    if response.status_code == 200:
        response_200 = RegistriesList.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[RegistriesList]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    name: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
) -> Response[RegistriesList]:
    kwargs = _get_kwargs(
        client=client,
        name=name,
        modified_at=modified_at,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    name: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
) -> Optional[RegistriesList]:
    """ List registries """

    return sync_detailed(
        client=client,
        name=name,
        modified_at=modified_at,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    name: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
) -> Response[RegistriesList]:
    kwargs = _get_kwargs(
        client=client,
        name=name,
        modified_at=modified_at,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    name: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
) -> Optional[RegistriesList]:
    """ List registries """

    return (
        await asyncio_detailed(
            client=client,
            name=name,
            modified_at=modified_at,
        )
    ).parsed
