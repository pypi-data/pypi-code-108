from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.oligos_bulk_get import OligosBulkGet
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    oligo_ids: str,
) -> Dict[str, Any]:
    url = "{}/oligos:bulk-get".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {
        "oligoIds": oligo_ids,
    }

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[OligosBulkGet, BadRequestError]]:
    if response.status_code == 200:
        response_200 = OligosBulkGet.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[OligosBulkGet, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    oligo_ids: str,
) -> Response[Union[OligosBulkGet, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        oligo_ids=oligo_ids,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    oligo_ids: str,
) -> Optional[Union[OligosBulkGet, BadRequestError]]:
    """ Bulk get Oligos by ID """

    return sync_detailed(
        client=client,
        oligo_ids=oligo_ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    oligo_ids: str,
) -> Response[Union[OligosBulkGet, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        oligo_ids=oligo_ids,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    oligo_ids: str,
) -> Optional[Union[OligosBulkGet, BadRequestError]]:
    """ Bulk get Oligos by ID """

    return (
        await asyncio_detailed(
            client=client,
            oligo_ids=oligo_ids,
        )
    ).parsed
