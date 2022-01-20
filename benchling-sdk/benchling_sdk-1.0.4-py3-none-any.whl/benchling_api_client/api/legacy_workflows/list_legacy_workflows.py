from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.legacy_workflow_list import LegacyWorkflowList
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/legacy-workflows".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[LegacyWorkflowList]:
    if response.status_code == 200:
        response_200 = LegacyWorkflowList.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[LegacyWorkflowList]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
) -> Response[LegacyWorkflowList]:
    kwargs = _get_kwargs(
        client=client,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
) -> Optional[LegacyWorkflowList]:
    """ List legacy workflows """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
) -> Response[LegacyWorkflowList]:
    kwargs = _get_kwargs(
        client=client,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
) -> Optional[LegacyWorkflowList]:
    """ List legacy workflows """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
