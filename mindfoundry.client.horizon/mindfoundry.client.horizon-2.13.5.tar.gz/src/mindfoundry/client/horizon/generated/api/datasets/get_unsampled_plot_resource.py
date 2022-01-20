from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.date_value_series import DateValueSeries
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    id: int,
    column_id: int,
    tail: Union[Unset, bool] = False,
    timestamp: Union[Unset, None, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/datasets/{id}/{columnId}/unsampled".format(
        client.base_url, id=id, columnId=column_id
    )

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {
        "tail": tail,
        "timestamp": timestamp,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[DateValueSeries]:
    if response.status_code == 200:
        response_200 = DateValueSeries.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[DateValueSeries]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    id: int,
    column_id: int,
    tail: Union[Unset, bool] = False,
    timestamp: Union[Unset, None, str] = UNSET,
) -> Response[DateValueSeries]:
    kwargs = _get_kwargs(
        client=client,
        id=id,
        column_id=column_id,
        tail=tail,
        timestamp=timestamp,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    id: int,
    column_id: int,
    tail: Union[Unset, bool] = False,
    timestamp: Union[Unset, None, str] = UNSET,
) -> Optional[DateValueSeries]:
    """You must either specify a `timestamp` or set `tail=true`."""

    return sync_detailed(
        client=client,
        id=id,
        column_id=column_id,
        tail=tail,
        timestamp=timestamp,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    id: int,
    column_id: int,
    tail: Union[Unset, bool] = False,
    timestamp: Union[Unset, None, str] = UNSET,
) -> Response[DateValueSeries]:
    kwargs = _get_kwargs(
        client=client,
        id=id,
        column_id=column_id,
        tail=tail,
        timestamp=timestamp,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    id: int,
    column_id: int,
    tail: Union[Unset, bool] = False,
    timestamp: Union[Unset, None, str] = UNSET,
) -> Optional[DateValueSeries]:
    """You must either specify a `timestamp` or set `tail=true`."""

    return (
        await asyncio_detailed(
            client=client,
            id=id,
            column_id=column_id,
            tail=tail,
            timestamp=timestamp,
        )
    ).parsed
