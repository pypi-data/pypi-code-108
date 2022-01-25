from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.collaborations_paginated_list import CollaborationsPaginatedList
from ...models.not_found_error import NotFoundError
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    worklist_id: str,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/worklists/{worklist_id}/collaborations".format(client.base_url, worklist_id=worklist_id)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[CollaborationsPaginatedList, BadRequestError, NotFoundError]]:
    if response.status_code == 200:
        response_200 = CollaborationsPaginatedList.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[CollaborationsPaginatedList, BadRequestError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    worklist_id: str,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
) -> Response[Union[CollaborationsPaginatedList, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        worklist_id=worklist_id,
        page_size=page_size,
        next_token=next_token,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    worklist_id: str,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
) -> Optional[Union[CollaborationsPaginatedList, BadRequestError, NotFoundError]]:
    """Returns information about collaborations on the specified Worklists."""

    return sync_detailed(
        client=client,
        worklist_id=worklist_id,
        page_size=page_size,
        next_token=next_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    worklist_id: str,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
) -> Response[Union[CollaborationsPaginatedList, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        worklist_id=worklist_id,
        page_size=page_size,
        next_token=next_token,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    worklist_id: str,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
) -> Optional[Union[CollaborationsPaginatedList, BadRequestError, NotFoundError]]:
    """Returns information about collaborations on the specified Worklists."""

    return (
        await asyncio_detailed(
            client=client,
            worklist_id=worklist_id,
            page_size=page_size,
            next_token=next_token,
        )
    ).parsed
