from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.not_found_error import NotFoundError
from ...models.workflow_output import WorkflowOutput
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    workflow_output_id: str,
) -> Dict[str, Any]:
    url = "{}/workflow-outputs/{workflow_output_id}".format(
        client.base_url, workflow_output_id=workflow_output_id
    )

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[WorkflowOutput, NotFoundError]]:
    if response.status_code == 200:
        response_200 = WorkflowOutput.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[WorkflowOutput, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    workflow_output_id: str,
) -> Response[Union[WorkflowOutput, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        workflow_output_id=workflow_output_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    workflow_output_id: str,
) -> Optional[Union[WorkflowOutput, NotFoundError]]:
    """ Get a workflow output """

    return sync_detailed(
        client=client,
        workflow_output_id=workflow_output_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    workflow_output_id: str,
) -> Response[Union[WorkflowOutput, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        workflow_output_id=workflow_output_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    workflow_output_id: str,
) -> Optional[Union[WorkflowOutput, NotFoundError]]:
    """ Get a workflow output """

    return (
        await asyncio_detailed(
            client=client,
            workflow_output_id=workflow_output_id,
        )
    ).parsed
