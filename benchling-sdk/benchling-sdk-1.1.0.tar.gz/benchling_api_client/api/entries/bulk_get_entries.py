from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.entries import Entries
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    entry_ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/entries:bulk-get".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if not isinstance(entry_ids, Unset) and entry_ids is not None:
        params["entryIds"] = entry_ids
    if not isinstance(display_ids, Unset) and display_ids is not None:
        params["displayIds"] = display_ids

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Entries, BadRequestError]]:
    if response.status_code == 200:
        response_200 = Entries.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Entries, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    entry_ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
) -> Response[Union[Entries, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        entry_ids=entry_ids,
        display_ids=display_ids,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    entry_ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
) -> Optional[Union[Entries, BadRequestError]]:
    """ Get notebook entries using entry IDs or display IDs """

    return sync_detailed(
        client=client,
        entry_ids=entry_ids,
        display_ids=display_ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    entry_ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
) -> Response[Union[Entries, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        entry_ids=entry_ids,
        display_ids=display_ids,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    entry_ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
) -> Optional[Union[Entries, BadRequestError]]:
    """ Get notebook entries using entry IDs or display IDs """

    return (
        await asyncio_detailed(
            client=client,
            entry_ids=entry_ids,
            display_ids=display_ids,
        )
    ).parsed
