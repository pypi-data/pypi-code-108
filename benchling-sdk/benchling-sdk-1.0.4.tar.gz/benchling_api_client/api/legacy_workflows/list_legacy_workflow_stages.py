from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.legacy_workflow_stage_list import LegacyWorkflowStageList
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    legacy_workflow_id: str,
) -> Dict[str, Any]:
    url = "{}/legacy-workflows/{legacy_workflow_id}/workflow-stages".format(
        client.base_url, legacy_workflow_id=legacy_workflow_id
    )

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[LegacyWorkflowStageList]:
    if response.status_code == 200:
        response_200 = LegacyWorkflowStageList.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[LegacyWorkflowStageList]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    legacy_workflow_id: str,
) -> Response[LegacyWorkflowStageList]:
    kwargs = _get_kwargs(
        client=client,
        legacy_workflow_id=legacy_workflow_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    legacy_workflow_id: str,
) -> Optional[LegacyWorkflowStageList]:
    """ List legacy workflow stages """

    return sync_detailed(
        client=client,
        legacy_workflow_id=legacy_workflow_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    legacy_workflow_id: str,
) -> Response[LegacyWorkflowStageList]:
    kwargs = _get_kwargs(
        client=client,
        legacy_workflow_id=legacy_workflow_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    legacy_workflow_id: str,
) -> Optional[LegacyWorkflowStageList]:
    """ List legacy workflow stages """

    return (
        await asyncio_detailed(
            client=client,
            legacy_workflow_id=legacy_workflow_id,
        )
    ).parsed
