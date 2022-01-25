from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.workflow_stage_list import WorkflowStageList
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    workflow_id: str,
) -> Dict[str, Any]:
    url = "{}/workflows/{workflow_id}/workflow-stages".format(client.base_url, workflow_id=workflow_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[WorkflowStageList]:
    if response.status_code == 200:
        response_200 = WorkflowStageList.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[WorkflowStageList]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    workflow_id: str,
) -> Response[WorkflowStageList]:
    kwargs = _get_kwargs(
        client=client,
        workflow_id=workflow_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    workflow_id: str,
) -> Optional[WorkflowStageList]:
    """ List workflow stages """

    return sync_detailed(
        client=client,
        workflow_id=workflow_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    workflow_id: str,
) -> Response[WorkflowStageList]:
    kwargs = _get_kwargs(
        client=client,
        workflow_id=workflow_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    workflow_id: str,
) -> Optional[WorkflowStageList]:
    """ List workflow stages """

    return (
        await asyncio_detailed(
            client=client,
            workflow_id=workflow_id,
        )
    ).parsed
