from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.not_found_error import NotFoundError
from ...models.plate import Plate
from ...models.plate_update import PlateUpdate
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    plate_id: str,
    json_body: PlateUpdate,
    returning: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/plates/{plate_id}".format(client.base_url, plate_id=plate_id)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if not isinstance(returning, Unset) and returning is not None:
        params["returning"] = returning

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Plate, BadRequestError, NotFoundError]]:
    if response.status_code == 200:
        response_200 = Plate.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Plate, BadRequestError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    plate_id: str,
    json_body: PlateUpdate,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[Plate, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        plate_id=plate_id,
        json_body=json_body,
        returning=returning,
    )

    response = httpx.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    plate_id: str,
    json_body: PlateUpdate,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[Plate, BadRequestError, NotFoundError]]:
    """ Update a plate """

    return sync_detailed(
        client=client,
        plate_id=plate_id,
        json_body=json_body,
        returning=returning,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    plate_id: str,
    json_body: PlateUpdate,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[Plate, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        plate_id=plate_id,
        json_body=json_body,
        returning=returning,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    plate_id: str,
    json_body: PlateUpdate,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[Plate, BadRequestError, NotFoundError]]:
    """ Update a plate """

    return (
        await asyncio_detailed(
            client=client,
            plate_id=plate_id,
            json_body=json_body,
            returning=returning,
        )
    ).parsed
