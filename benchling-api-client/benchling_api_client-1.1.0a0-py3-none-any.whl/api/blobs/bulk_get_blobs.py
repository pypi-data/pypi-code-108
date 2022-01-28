from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.blobs_bulk_get import BlobsBulkGet
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    blob_ids: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/blobs:bulk-get".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if not isinstance(blob_ids, Unset) and blob_ids is not None:
        params["blobIds"] = blob_ids

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[BlobsBulkGet, BadRequestError]]:
    if response.status_code == 200:
        response_200 = BlobsBulkGet.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[BlobsBulkGet, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    blob_ids: Union[Unset, str] = UNSET,
) -> Response[Union[BlobsBulkGet, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        blob_ids=blob_ids,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    blob_ids: Union[Unset, str] = UNSET,
) -> Optional[Union[BlobsBulkGet, BadRequestError]]:
    """ Bulk get Blobs by UUID """

    return sync_detailed(
        client=client,
        blob_ids=blob_ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    blob_ids: Union[Unset, str] = UNSET,
) -> Response[Union[BlobsBulkGet, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        blob_ids=blob_ids,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    blob_ids: Union[Unset, str] = UNSET,
) -> Optional[Union[BlobsBulkGet, BadRequestError]]:
    """ Bulk get Blobs by UUID """

    return (
        await asyncio_detailed(
            client=client,
            blob_ids=blob_ids,
        )
    ).parsed
