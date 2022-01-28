from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.plate import Plate
from ...models.plate_create import PlateCreate
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    json_body: PlateCreate,
    returning: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/plates".format(client.base_url)

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


def _parse_response(*, response: httpx.Response) -> Optional[Union[Plate, BadRequestError]]:
    if response.status_code == 201:
        response_201 = Plate.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Plate, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: PlateCreate,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[Plate, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        returning=returning,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    json_body: PlateCreate,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[Plate, BadRequestError]]:
    """ Create a plate """

    return sync_detailed(
        client=client,
        json_body=json_body,
        returning=returning,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: PlateCreate,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[Plate, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        returning=returning,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    json_body: PlateCreate,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[Plate, BadRequestError]]:
    """ Create a plate """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
            returning=returning,
        )
    ).parsed
