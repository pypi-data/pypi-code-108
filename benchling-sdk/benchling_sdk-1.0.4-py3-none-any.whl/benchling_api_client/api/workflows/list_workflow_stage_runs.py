from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.workflow_stage_run_list import WorkflowStageRunList
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    stage_id: str,
) -> Dict[str, Any]:
    url = "{}/workflow-stages/{stage_id}/workflow-stage-runs".format(client.base_url, stage_id=stage_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[WorkflowStageRunList]:
    if response.status_code == 200:
        response_200 = WorkflowStageRunList.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[WorkflowStageRunList]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    stage_id: str,
) -> Response[WorkflowStageRunList]:
    kwargs = _get_kwargs(
        client=client,
        stage_id=stage_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    stage_id: str,
) -> Optional[WorkflowStageRunList]:
    """ List workflow stage runs """

    return sync_detailed(
        client=client,
        stage_id=stage_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    stage_id: str,
) -> Response[WorkflowStageRunList]:
    kwargs = _get_kwargs(
        client=client,
        stage_id=stage_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    stage_id: str,
) -> Optional[WorkflowStageRunList]:
    """ List workflow stage runs """

    return (
        await asyncio_detailed(
            client=client,
            stage_id=stage_id,
        )
    ).parsed
