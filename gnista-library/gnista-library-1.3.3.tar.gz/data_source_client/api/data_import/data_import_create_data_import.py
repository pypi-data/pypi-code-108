from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.data_import_request import DataImportRequest
from ...models.problem_details import ProblemDetails
from ...types import Response


def _get_kwargs(
    data_import_id: str,
    *,
    client: Client,
    json_body: DataImportRequest,
) -> Dict[str, Any]:
    url = "{}/DataImport/{dataImportId}".format(client.base_url, dataImportId=data_import_id)

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


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, ProblemDetails]]:
    if response.status_code == 202:
        response_202 = None

        return response_202
    if response.status_code == 400:
        response_400 = ProblemDetails.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = ProblemDetails.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = ProblemDetails.from_dict(response.json())

        return response_403
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, ProblemDetails]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    data_import_id: str,
    *,
    client: Client,
    json_body: DataImportRequest,
) -> Response[Union[Any, ProblemDetails]]:
    kwargs = _get_kwargs(
        data_import_id=data_import_id,
        client=client,
        json_body=json_body,
    )

    response = httpx.post(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    data_import_id: str,
    *,
    client: Client,
    json_body: DataImportRequest,
) -> Optional[Union[Any, ProblemDetails]]:
    """ """

    return sync_detailed(
        data_import_id=data_import_id,
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    data_import_id: str,
    *,
    client: Client,
    json_body: DataImportRequest,
) -> Response[Union[Any, ProblemDetails]]:
    kwargs = _get_kwargs(
        data_import_id=data_import_id,
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    data_import_id: str,
    *,
    client: Client,
    json_body: DataImportRequest,
) -> Optional[Union[Any, ProblemDetails]]:
    """ """

    return (
        await asyncio_detailed(
            data_import_id=data_import_id,
            client=client,
            json_body=json_body,
        )
    ).parsed
