from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.not_found_error import NotFoundError
from ...models.worklist import Worklist
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    worklist_id: str,
) -> Dict[str, Any]:
    url = "{}/worklists/{worklist_id}".format(client.base_url, worklist_id=worklist_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Worklist, NotFoundError]]:
    if response.status_code == 200:
        response_200 = Worklist.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Worklist, NotFoundError]]:
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
) -> Response[Union[Worklist, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        worklist_id=worklist_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    worklist_id: str,
) -> Optional[Union[Worklist, NotFoundError]]:
    """ Get a worklist by ID """

    return sync_detailed(
        client=client,
        worklist_id=worklist_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    worklist_id: str,
) -> Response[Union[Worklist, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        worklist_id=worklist_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    worklist_id: str,
) -> Optional[Union[Worklist, NotFoundError]]:
    """ Get a worklist by ID """

    return (
        await asyncio_detailed(
            client=client,
            worklist_id=worklist_id,
        )
    ).parsed
