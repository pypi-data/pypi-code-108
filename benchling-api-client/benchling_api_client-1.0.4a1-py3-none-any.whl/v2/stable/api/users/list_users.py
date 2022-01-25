from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.list_users_sort import ListUsersSort
from ...models.users_paginated_list import UsersPaginatedList
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    ids: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    member_of: Union[Unset, str] = UNSET,
    admin_of: Union[Unset, str] = UNSET,
    handles: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListUsersSort] = ListUsersSort.MODIFIEDATDESC,
) -> Dict[str, Any]:
    url = "{}/users".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_sort: Union[Unset, int] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params: Dict[str, Any] = {}
    if not isinstance(ids, Unset) and ids is not None:
        params["ids"] = ids
    if not isinstance(name, Unset) and name is not None:
        params["name"] = name
    if not isinstance(name_includes, Unset) and name_includes is not None:
        params["nameIncludes"] = name_includes
    if not isinstance(namesany_of, Unset) and namesany_of is not None:
        params["names.anyOf"] = namesany_of
    if not isinstance(namesany_ofcase_sensitive, Unset) and namesany_ofcase_sensitive is not None:
        params["names.anyOf.caseSensitive"] = namesany_ofcase_sensitive
    if not isinstance(modified_at, Unset) and modified_at is not None:
        params["modifiedAt"] = modified_at
    if not isinstance(member_of, Unset) and member_of is not None:
        params["memberOf"] = member_of
    if not isinstance(admin_of, Unset) and admin_of is not None:
        params["adminOf"] = admin_of
    if not isinstance(handles, Unset) and handles is not None:
        params["handles"] = handles
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(json_sort, Unset) and json_sort is not None:
        params["sort"] = json_sort

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[UsersPaginatedList, BadRequestError]]:
    if response.status_code == 200:
        response_200 = UsersPaginatedList.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[UsersPaginatedList, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    ids: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    member_of: Union[Unset, str] = UNSET,
    admin_of: Union[Unset, str] = UNSET,
    handles: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListUsersSort] = ListUsersSort.MODIFIEDATDESC,
) -> Response[Union[UsersPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        ids=ids,
        name=name,
        name_includes=name_includes,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        modified_at=modified_at,
        member_of=member_of,
        admin_of=admin_of,
        handles=handles,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    ids: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    member_of: Union[Unset, str] = UNSET,
    admin_of: Union[Unset, str] = UNSET,
    handles: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListUsersSort] = ListUsersSort.MODIFIEDATDESC,
) -> Optional[Union[UsersPaginatedList, BadRequestError]]:
    """Returns all users that the caller has permission to view. The following roles have view permission:
    - tenant admins
    - members of the user's organizations
    """

    return sync_detailed(
        client=client,
        ids=ids,
        name=name,
        name_includes=name_includes,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        modified_at=modified_at,
        member_of=member_of,
        admin_of=admin_of,
        handles=handles,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    ids: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    member_of: Union[Unset, str] = UNSET,
    admin_of: Union[Unset, str] = UNSET,
    handles: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListUsersSort] = ListUsersSort.MODIFIEDATDESC,
) -> Response[Union[UsersPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        ids=ids,
        name=name,
        name_includes=name_includes,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        modified_at=modified_at,
        member_of=member_of,
        admin_of=admin_of,
        handles=handles,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    ids: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    name_includes: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    member_of: Union[Unset, str] = UNSET,
    admin_of: Union[Unset, str] = UNSET,
    handles: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    sort: Union[Unset, ListUsersSort] = ListUsersSort.MODIFIEDATDESC,
) -> Optional[Union[UsersPaginatedList, BadRequestError]]:
    """Returns all users that the caller has permission to view. The following roles have view permission:
    - tenant admins
    - members of the user's organizations
    """

    return (
        await asyncio_detailed(
            client=client,
            ids=ids,
            name=name,
            name_includes=name_includes,
            namesany_of=namesany_of,
            namesany_ofcase_sensitive=namesany_ofcase_sensitive,
            modified_at=modified_at,
            member_of=member_of,
            admin_of=admin_of,
            handles=handles,
            page_size=page_size,
            next_token=next_token,
            sort=sort,
        )
    ).parsed
