from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.legacy_workflow_sample_list import LegacyWorkflowSampleList
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    stage_run_id: str,
) -> Dict[str, Any]:
    url = "{}/legacy-workflow-stage-runs/{stage_run_id}/registered-samples".format(
        client.base_url, stage_run_id=stage_run_id
    )

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[LegacyWorkflowSampleList]:
    if response.status_code == 200:
        response_200 = LegacyWorkflowSampleList.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[LegacyWorkflowSampleList]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    stage_run_id: str,
) -> Response[LegacyWorkflowSampleList]:
    kwargs = _get_kwargs(
        client=client,
        stage_run_id=stage_run_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    stage_run_id: str,
) -> Optional[LegacyWorkflowSampleList]:
    """ List legacy workflow stage run registered samples """

    return sync_detailed(
        client=client,
        stage_run_id=stage_run_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    stage_run_id: str,
) -> Response[LegacyWorkflowSampleList]:
    kwargs = _get_kwargs(
        client=client,
        stage_run_id=stage_run_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    stage_run_id: str,
) -> Optional[LegacyWorkflowSampleList]:
    """ List legacy workflow stage run registered samples """

    return (
        await asyncio_detailed(
            client=client,
            stage_run_id=stage_run_id,
        )
    ).parsed
