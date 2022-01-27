from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.series_overview_schema import SeriesOverviewSchema
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    id: int,
    column_id: int,
) -> Dict[str, Any]:
    url = "{}/datasets/{id}/{columnId}/plot".format(client.base_url, id=id, columnId=column_id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[SeriesOverviewSchema]:
    if response.status_code == 200:
        response_200 = SeriesOverviewSchema.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[SeriesOverviewSchema]:
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
) -> Response[SeriesOverviewSchema]:
    kwargs = _get_kwargs(
        client=client,
        id=id,
        column_id=column_id,
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
) -> Optional[SeriesOverviewSchema]:
    """  """

    return sync_detailed(
        client=client,
        id=id,
        column_id=column_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    id: int,
    column_id: int,
) -> Response[SeriesOverviewSchema]:
    kwargs = _get_kwargs(
        client=client,
        id=id,
        column_id=column_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    id: int,
    column_id: int,
) -> Optional[SeriesOverviewSchema]:
    """  """

    return (
        await asyncio_detailed(
            client=client,
            id=id,
            column_id=column_id,
        )
    ).parsed
