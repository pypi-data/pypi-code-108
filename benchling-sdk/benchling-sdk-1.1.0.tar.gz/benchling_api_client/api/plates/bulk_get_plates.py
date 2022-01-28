from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.not_found_error import NotFoundError
from ...models.plates_bulk_get import PlatesBulkGet
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    plate_ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/plates:bulk-get".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if not isinstance(plate_ids, Unset) and plate_ids is not None:
        params["plateIds"] = plate_ids
    if not isinstance(barcodes, Unset) and barcodes is not None:
        params["barcodes"] = barcodes
    if not isinstance(returning, Unset) and returning is not None:
        params["returning"] = returning

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[PlatesBulkGet, BadRequestError, NotFoundError]]:
    if response.status_code == 200:
        response_200 = PlatesBulkGet.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[PlatesBulkGet, BadRequestError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    plate_ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[PlatesBulkGet, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        plate_ids=plate_ids,
        barcodes=barcodes,
        returning=returning,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    plate_ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[PlatesBulkGet, BadRequestError, NotFoundError]]:
    """ BulkGet plates """

    return sync_detailed(
        client=client,
        plate_ids=plate_ids,
        barcodes=barcodes,
        returning=returning,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    plate_ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[PlatesBulkGet, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        plate_ids=plate_ids,
        barcodes=barcodes,
        returning=returning,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    plate_ids: Union[Unset, str] = UNSET,
    barcodes: Union[Unset, str] = UNSET,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[PlatesBulkGet, BadRequestError, NotFoundError]]:
    """ BulkGet plates """

    return (
        await asyncio_detailed(
            client=client,
            plate_ids=plate_ids,
            barcodes=barcodes,
            returning=returning,
        )
    ).parsed
