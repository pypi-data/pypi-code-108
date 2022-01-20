from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.not_found_error import NotFoundError
from ...models.request_tasks_bulk_update_request import RequestTasksBulkUpdateRequest
from ...models.request_tasks_bulk_update_response import RequestTasksBulkUpdateResponse
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    request_id: str,
    json_body: RequestTasksBulkUpdateRequest,
) -> Dict[str, Any]:
    url = "{}/requests/{request_id}/tasks:bulk-update".format(client.base_url, request_id=request_id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[RequestTasksBulkUpdateResponse, NotFoundError]]:
    if response.status_code == 200:
        response_200 = RequestTasksBulkUpdateResponse.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[RequestTasksBulkUpdateResponse, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    request_id: str,
    json_body: RequestTasksBulkUpdateRequest,
) -> Response[Union[RequestTasksBulkUpdateResponse, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        request_id=request_id,
        json_body=json_body,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    request_id: str,
    json_body: RequestTasksBulkUpdateRequest,
) -> Optional[Union[RequestTasksBulkUpdateResponse, NotFoundError]]:
    """ Bulk update tasks for a request """

    return sync_detailed(
        client=client,
        request_id=request_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    request_id: str,
    json_body: RequestTasksBulkUpdateRequest,
) -> Response[Union[RequestTasksBulkUpdateResponse, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        request_id=request_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    request_id: str,
    json_body: RequestTasksBulkUpdateRequest,
) -> Optional[Union[RequestTasksBulkUpdateResponse, NotFoundError]]:
    """ Bulk update tasks for a request """

    return (
        await asyncio_detailed(
            client=client,
            request_id=request_id,
            json_body=json_body,
        )
    ).parsed
