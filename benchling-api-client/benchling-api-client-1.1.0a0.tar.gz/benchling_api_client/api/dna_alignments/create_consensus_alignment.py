from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.async_task_link import AsyncTaskLink
from ...models.dna_consensus_alignment_create import DnaConsensusAlignmentCreate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: DnaConsensusAlignmentCreate,
) -> Dict[str, Any]:
    url = "{}/dna-alignments:create-consensus-alignment".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[AsyncTaskLink]:
    if response.status_code == 202:
        response_202 = AsyncTaskLink.from_dict(response.json())

        return response_202
    return None


def _build_response(*, response: httpx.Response) -> Response[AsyncTaskLink]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: DnaConsensusAlignmentCreate,
) -> Response[AsyncTaskLink]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    json_body: DnaConsensusAlignmentCreate,
) -> Optional[AsyncTaskLink]:
    """ Create a consensus DNA alignment """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: DnaConsensusAlignmentCreate,
) -> Response[AsyncTaskLink]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    json_body: DnaConsensusAlignmentCreate,
) -> Optional[AsyncTaskLink]:
    """ Create a consensus DNA alignment """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
