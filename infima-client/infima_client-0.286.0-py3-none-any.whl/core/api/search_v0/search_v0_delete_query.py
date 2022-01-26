from typing import Any, Dict, List, Optional, Union, cast

import httpx

from infima_client.core.client import Client
from infima_client.core.models.google.rpc.status import GoogleRpcStatus
from infima_client.core.models.search.v0.delete_query_request import (
    SearchV0DeleteQueryRequest,
)
from infima_client.core.models.search.v0.delete_query_response import (
    SearchV0DeleteQueryResponse,
)
from infima_client.core.types import UNSET, Response


def _get_kwargs(
    *,
    client: Client,
    json_body: SearchV0DeleteQueryRequest,
) -> Dict[str, Any]:
    url = "{}/api/v0/search/delete_query".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[GoogleRpcStatus, SearchV0DeleteQueryResponse]]:
    if response.status_code == 200:
        response_200 = SearchV0DeleteQueryResponse.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = GoogleRpcStatus.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = GoogleRpcStatus.from_dict(response.json())

        return response_401
    if response.status_code == 404:
        response_404 = GoogleRpcStatus.from_dict(response.json())

        return response_404
    if response.status_code == 408:
        response_408 = GoogleRpcStatus.from_dict(response.json())

        return response_408
    if response.status_code == 500:
        response_500 = GoogleRpcStatus.from_dict(response.json())

        return response_500
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[GoogleRpcStatus, SearchV0DeleteQueryResponse]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: SearchV0DeleteQueryRequest,
) -> Response[Union[GoogleRpcStatus, SearchV0DeleteQueryResponse]]:
    """
    Args:
        json_body (SearchV0DeleteQueryRequest):

    Returns:
        Response[Union[GoogleRpcStatus, SearchV0DeleteQueryResponse]]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    response = httpx.post(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    json_body: SearchV0DeleteQueryRequest,
) -> Optional[Union[GoogleRpcStatus, SearchV0DeleteQueryResponse]]:
    """
    Args:
        json_body (SearchV0DeleteQueryRequest):

    Returns:
        Response[Union[GoogleRpcStatus, SearchV0DeleteQueryResponse]]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: SearchV0DeleteQueryRequest,
) -> Response[Union[GoogleRpcStatus, SearchV0DeleteQueryResponse]]:
    """
    Args:
        json_body (SearchV0DeleteQueryRequest):

    Returns:
        Response[Union[GoogleRpcStatus, SearchV0DeleteQueryResponse]]
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    json_body: SearchV0DeleteQueryRequest,
) -> Optional[Union[GoogleRpcStatus, SearchV0DeleteQueryResponse]]:
    """
    Args:
        json_body (SearchV0DeleteQueryRequest):

    Returns:
        Response[Union[GoogleRpcStatus, SearchV0DeleteQueryResponse]]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
