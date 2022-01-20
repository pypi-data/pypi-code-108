from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.not_found_error import NotFoundError
from ...models.requests_bulk_get import RequestsBulkGet
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    request_ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/requests:bulk-get".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if not isinstance(request_ids, Unset) and request_ids is not None:
        params["requestIds"] = request_ids
    if not isinstance(display_ids, Unset) and display_ids is not None:
        params["displayIds"] = display_ids

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[RequestsBulkGet, NotFoundError]]:
    if response.status_code == 200:
        response_200 = RequestsBulkGet.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[RequestsBulkGet, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    request_ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
) -> Response[Union[RequestsBulkGet, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        request_ids=request_ids,
        display_ids=display_ids,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    request_ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
) -> Optional[Union[RequestsBulkGet, NotFoundError]]:
    """ Bulk get requests by API ID or display ID """

    return sync_detailed(
        client=client,
        request_ids=request_ids,
        display_ids=display_ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    request_ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
) -> Response[Union[RequestsBulkGet, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        request_ids=request_ids,
        display_ids=display_ids,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    request_ids: Union[Unset, str] = UNSET,
    display_ids: Union[Unset, str] = UNSET,
) -> Optional[Union[RequestsBulkGet, NotFoundError]]:
    """ Bulk get requests by API ID or display ID """

    return (
        await asyncio_detailed(
            client=client,
            request_ids=request_ids,
            display_ids=display_ids,
        )
    ).parsed
