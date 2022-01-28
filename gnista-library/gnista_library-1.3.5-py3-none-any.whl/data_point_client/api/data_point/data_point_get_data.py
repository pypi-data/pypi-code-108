from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.get_data_request import GetDataRequest
from ...models.get_data_response import GetDataResponse
from ...models.problem_details import ProblemDetails
from ...types import Response


def _get_kwargs(
    data_point_id: str,
    *,
    client: Client,
    json_body: GetDataRequest,
) -> Dict[str, Any]:
    url = "{}/DataPoint/{dataPointId}/data/find".format(client.base_url, dataPointId=data_point_id)

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


def _parse_response(*, response: httpx.Response) -> Optional[Union[GetDataResponse, ProblemDetails]]:
    if response.status_code == 200:
        response_200 = GetDataResponse.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = ProblemDetails.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = ProblemDetails.from_dict(response.json())

        return response_403
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[GetDataResponse, ProblemDetails]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    data_point_id: str,
    *,
    client: Client,
    json_body: GetDataRequest,
) -> Response[Union[GetDataResponse, ProblemDetails]]:
    kwargs = _get_kwargs(
        data_point_id=data_point_id,
        client=client,
        json_body=json_body,
    )

    response = httpx.post(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    data_point_id: str,
    *,
    client: Client,
    json_body: GetDataRequest,
) -> Optional[Union[GetDataResponse, ProblemDetails]]:
    """ """

    return sync_detailed(
        data_point_id=data_point_id,
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    data_point_id: str,
    *,
    client: Client,
    json_body: GetDataRequest,
) -> Response[Union[GetDataResponse, ProblemDetails]]:
    kwargs = _get_kwargs(
        data_point_id=data_point_id,
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    data_point_id: str,
    *,
    client: Client,
    json_body: GetDataRequest,
) -> Optional[Union[GetDataResponse, ProblemDetails]]:
    """ """

    return (
        await asyncio_detailed(
            data_point_id=data_point_id,
            client=client,
            json_body=json_body,
        )
    ).parsed
