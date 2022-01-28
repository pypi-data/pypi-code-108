from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.not_found_error import NotFoundError
from ...models.workflow_task import WorkflowTask
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    workflow_task_id: str,
) -> Dict[str, Any]:
    url = "{}/workflow-tasks/{workflow_task_id}:copy".format(
        client.base_url, workflow_task_id=workflow_task_id
    )

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[WorkflowTask, BadRequestError, NotFoundError]]:
    if response.status_code == 201:
        response_201 = WorkflowTask.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[WorkflowTask, BadRequestError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    workflow_task_id: str,
) -> Response[Union[WorkflowTask, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        workflow_task_id=workflow_task_id,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    workflow_task_id: str,
) -> Optional[Union[WorkflowTask, BadRequestError, NotFoundError]]:
    """ Creates a new workflow task based on the provided task """

    return sync_detailed(
        client=client,
        workflow_task_id=workflow_task_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    workflow_task_id: str,
) -> Response[Union[WorkflowTask, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        workflow_task_id=workflow_task_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    workflow_task_id: str,
) -> Optional[Union[WorkflowTask, BadRequestError, NotFoundError]]:
    """ Creates a new workflow task based on the provided task """

    return (
        await asyncio_detailed(
            client=client,
            workflow_task_id=workflow_task_id,
        )
    ).parsed
