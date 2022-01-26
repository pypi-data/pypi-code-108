from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.list_worklists_sort import ListWorklistsSort
from ...models.worklist_type import WorklistType
from ...models.worklists_paginated_list import WorklistsPaginatedList
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListWorklistsSort] = ListWorklistsSort.MODIFIEDATDESC,
    modified_at: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    worklist_type: Union[Unset, WorklistType] = UNSET,
) -> Dict[str, Any]:
    url = "{}/worklists".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_sort: Union[Unset, int] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    json_worklist_type: Union[Unset, int] = UNSET
    if not isinstance(worklist_type, Unset):
        json_worklist_type = worklist_type.value

    params: Dict[str, Any] = {}
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(json_sort, Unset) and json_sort is not None:
        params["sort"] = json_sort
    if not isinstance(modified_at, Unset) and modified_at is not None:
        params["modifiedAt"] = modified_at
    if not isinstance(ids, Unset) and ids is not None:
        params["ids"] = ids
    if not isinstance(json_worklist_type, Unset) and json_worklist_type is not None:
        params["worklistType"] = json_worklist_type

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[WorklistsPaginatedList, BadRequestError]]:
    if response.status_code == 200:
        response_200 = WorklistsPaginatedList.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[WorklistsPaginatedList, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListWorklistsSort] = ListWorklistsSort.MODIFIEDATDESC,
    modified_at: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    worklist_type: Union[Unset, WorklistType] = UNSET,
) -> Response[Union[WorklistsPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        modified_at=modified_at,
        ids=ids,
        worklist_type=worklist_type,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListWorklistsSort] = ListWorklistsSort.MODIFIEDATDESC,
    modified_at: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    worklist_type: Union[Unset, WorklistType] = UNSET,
) -> Optional[Union[WorklistsPaginatedList, BadRequestError]]:
    """List worklists. Individual items within a worklist are summarized."""

    return sync_detailed(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        modified_at=modified_at,
        ids=ids,
        worklist_type=worklist_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListWorklistsSort] = ListWorklistsSort.MODIFIEDATDESC,
    modified_at: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    worklist_type: Union[Unset, WorklistType] = UNSET,
) -> Response[Union[WorklistsPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        modified_at=modified_at,
        ids=ids,
        worklist_type=worklist_type,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListWorklistsSort] = ListWorklistsSort.MODIFIEDATDESC,
    modified_at: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    worklist_type: Union[Unset, WorklistType] = UNSET,
) -> Optional[Union[WorklistsPaginatedList, BadRequestError]]:
    """List worklists. Individual items within a worklist are summarized."""

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            next_token=next_token,
            sort=sort,
            modified_at=modified_at,
            ids=ids,
            worklist_type=worklist_type,
        )
    ).parsed
