from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.events_paginated_list import EventsPaginatedList
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    created_atgte: Union[Unset, str] = UNSET,
    starting_after: Union[Unset, str] = UNSET,
    event_types: Union[Unset, str] = UNSET,
    poll: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    url = "{}/events".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(created_atgte, Unset) and created_atgte is not None:
        params["createdAt.gte"] = created_atgte
    if not isinstance(starting_after, Unset) and starting_after is not None:
        params["startingAfter"] = starting_after
    if not isinstance(event_types, Unset) and event_types is not None:
        params["eventTypes"] = event_types
    if not isinstance(poll, Unset) and poll is not None:
        params["poll"] = poll

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[EventsPaginatedList, BadRequestError]]:
    if response.status_code == 200:
        response_200 = EventsPaginatedList.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[EventsPaginatedList, BadRequestError]]:
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
    created_atgte: Union[Unset, str] = UNSET,
    starting_after: Union[Unset, str] = UNSET,
    event_types: Union[Unset, str] = UNSET,
    poll: Union[Unset, bool] = UNSET,
) -> Response[Union[EventsPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        created_atgte=created_atgte,
        starting_after=starting_after,
        event_types=event_types,
        poll=poll,
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
    created_atgte: Union[Unset, str] = UNSET,
    starting_after: Union[Unset, str] = UNSET,
    event_types: Union[Unset, str] = UNSET,
    poll: Union[Unset, bool] = UNSET,
) -> Optional[Union[EventsPaginatedList, BadRequestError]]:
    """List Events

    ## Event Sort Order

    Events in Benchling are assigned a stable sort order that reflects when the event was processed (not created). The createdAt time is not the stable sorted order of events. For this reason event createdAt time may appear out of order.
    """

    return sync_detailed(
        client=client,
        page_size=page_size,
        next_token=next_token,
        created_atgte=created_atgte,
        starting_after=starting_after,
        event_types=event_types,
        poll=poll,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    created_atgte: Union[Unset, str] = UNSET,
    starting_after: Union[Unset, str] = UNSET,
    event_types: Union[Unset, str] = UNSET,
    poll: Union[Unset, bool] = UNSET,
) -> Response[Union[EventsPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        created_atgte=created_atgte,
        starting_after=starting_after,
        event_types=event_types,
        poll=poll,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    created_atgte: Union[Unset, str] = UNSET,
    starting_after: Union[Unset, str] = UNSET,
    event_types: Union[Unset, str] = UNSET,
    poll: Union[Unset, bool] = UNSET,
) -> Optional[Union[EventsPaginatedList, BadRequestError]]:
    """List Events

    ## Event Sort Order

    Events in Benchling are assigned a stable sort order that reflects when the event was processed (not created). The createdAt time is not the stable sorted order of events. For this reason event createdAt time may appear out of order.
    """

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            next_token=next_token,
            created_atgte=created_atgte,
            starting_after=starting_after,
            event_types=event_types,
            poll=poll,
        )
    ).parsed
