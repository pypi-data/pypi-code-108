from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.request_fulfillments_paginated_list import RequestFulfillmentsPaginatedList
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    entry_id: str,
    modified_at: Union[Unset, str] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
) -> Dict[str, Any]:
    url = "{}/request-fulfillments".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {
        "entryId": entry_id,
    }
    if not isinstance(modified_at, Unset) and modified_at is not None:
        params["modifiedAt"] = modified_at
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[RequestFulfillmentsPaginatedList, BadRequestError]]:
    if response.status_code == 200:
        response_200 = RequestFulfillmentsPaginatedList.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[RequestFulfillmentsPaginatedList, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    entry_id: str,
    modified_at: Union[Unset, str] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
) -> Response[Union[RequestFulfillmentsPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        entry_id=entry_id,
        modified_at=modified_at,
        next_token=next_token,
        page_size=page_size,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    entry_id: str,
    modified_at: Union[Unset, str] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
) -> Optional[Union[RequestFulfillmentsPaginatedList, BadRequestError]]:
    """ List Request Fulfillments """

    return sync_detailed(
        client=client,
        entry_id=entry_id,
        modified_at=modified_at,
        next_token=next_token,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    entry_id: str,
    modified_at: Union[Unset, str] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
) -> Response[Union[RequestFulfillmentsPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        entry_id=entry_id,
        modified_at=modified_at,
        next_token=next_token,
        page_size=page_size,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    entry_id: str,
    modified_at: Union[Unset, str] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
) -> Optional[Union[RequestFulfillmentsPaginatedList, BadRequestError]]:
    """ List Request Fulfillments """

    return (
        await asyncio_detailed(
            client=client,
            entry_id=entry_id,
            modified_at=modified_at,
            next_token=next_token,
            page_size=page_size,
        )
    ).parsed
