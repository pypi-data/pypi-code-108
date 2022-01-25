from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.list_projects_sort import ListProjectsSort
from ...models.projects_paginated_list import ProjectsPaginatedList
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    sort: Union[Unset, ListProjectsSort] = ListProjectsSort.MODIFIEDAT,
    archive_reason: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/projects".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_sort: Union[Unset, int] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params: Dict[str, Any] = {}
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size
    if not isinstance(json_sort, Unset) and json_sort is not None:
        params["sort"] = json_sort
    if not isinstance(archive_reason, Unset) and archive_reason is not None:
        params["archiveReason"] = archive_reason
    if not isinstance(ids, Unset) and ids is not None:
        params["ids"] = ids
    if not isinstance(name, Unset) and name is not None:
        params["name"] = name

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[ProjectsPaginatedList]:
    if response.status_code == 200:
        response_200 = ProjectsPaginatedList.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[ProjectsPaginatedList]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    sort: Union[Unset, ListProjectsSort] = ListProjectsSort.MODIFIEDAT,
    archive_reason: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
) -> Response[ProjectsPaginatedList]:
    kwargs = _get_kwargs(
        client=client,
        next_token=next_token,
        page_size=page_size,
        sort=sort,
        archive_reason=archive_reason,
        ids=ids,
        name=name,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    sort: Union[Unset, ListProjectsSort] = ListProjectsSort.MODIFIEDAT,
    archive_reason: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
) -> Optional[ProjectsPaginatedList]:
    """ List projects """

    return sync_detailed(
        client=client,
        next_token=next_token,
        page_size=page_size,
        sort=sort,
        archive_reason=archive_reason,
        ids=ids,
        name=name,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    sort: Union[Unset, ListProjectsSort] = ListProjectsSort.MODIFIEDAT,
    archive_reason: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
) -> Response[ProjectsPaginatedList]:
    kwargs = _get_kwargs(
        client=client,
        next_token=next_token,
        page_size=page_size,
        sort=sort,
        archive_reason=archive_reason,
        ids=ids,
        name=name,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    sort: Union[Unset, ListProjectsSort] = ListProjectsSort.MODIFIEDAT,
    archive_reason: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
) -> Optional[ProjectsPaginatedList]:
    """ List projects """

    return (
        await asyncio_detailed(
            client=client,
            next_token=next_token,
            page_size=page_size,
            sort=sort,
            archive_reason=archive_reason,
            ids=ids,
            name=name,
        )
    ).parsed
