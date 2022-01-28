from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    workflow_task_group_id: str,
) -> Dict[str, Any]:
    url = "{}/workflow-task-groups/{workflow_task_group_id}".format(
        client.base_url, workflow_task_group_id=workflow_task_group_id
    )

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[NotFoundError]:
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[NotFoundError]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    workflow_task_group_id: str,
) -> Response[NotFoundError]:
    kwargs = _get_kwargs(
        client=client,
        workflow_task_group_id=workflow_task_group_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    workflow_task_group_id: str,
) -> Optional[NotFoundError]:
    """ Get a workflow task group """

    return sync_detailed(
        client=client,
        workflow_task_group_id=workflow_task_group_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    workflow_task_group_id: str,
) -> Response[NotFoundError]:
    kwargs = _get_kwargs(
        client=client,
        workflow_task_group_id=workflow_task_group_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    workflow_task_group_id: str,
) -> Optional[NotFoundError]:
    """ Get a workflow task group """

    return (
        await asyncio_detailed(
            client=client,
            workflow_task_group_id=workflow_task_group_id,
        )
    ).parsed
