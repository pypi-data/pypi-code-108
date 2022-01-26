from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.data_import_response import DataImportResponse
from ...types import Response


def _get_kwargs(
    data_import_id: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/DataImport/{dataImportId}".format(client.base_url, dataImportId=data_import_id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[DataImportResponse]:
    if response.status_code == 200:
        response_200 = DataImportResponse.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[DataImportResponse]:
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
) -> Response[DataImportResponse]:
    kwargs = _get_kwargs(
        data_import_id=data_import_id,
        client=client,
    )

    response = httpx.get(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    data_import_id: str,
    *,
    client: Client,
) -> Optional[DataImportResponse]:
    """ """

    return sync_detailed(
        data_import_id=data_import_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    data_import_id: str,
    *,
    client: Client,
) -> Response[DataImportResponse]:
    kwargs = _get_kwargs(
        data_import_id=data_import_id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    data_import_id: str,
    *,
    client: Client,
) -> Optional[DataImportResponse]:
    """ """

    return (
        await asyncio_detailed(
            data_import_id=data_import_id,
            client=client,
        )
    ).parsed
