from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.box import Box
from ...models.box_update import BoxUpdate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    box_id: str,
    json_body: BoxUpdate,
) -> Dict[str, Any]:
    url = "{}/boxes/{box_id}".format(client.base_url, box_id=box_id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Box, BadRequestError]]:
    if response.status_code == 200:
        response_200 = Box.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Box, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    box_id: str,
    json_body: BoxUpdate,
) -> Response[Union[Box, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        box_id=box_id,
        json_body=json_body,
    )

    response = httpx.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    box_id: str,
    json_body: BoxUpdate,
) -> Optional[Union[Box, BadRequestError]]:
    """ Update a box """

    return sync_detailed(
        client=client,
        box_id=box_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    box_id: str,
    json_body: BoxUpdate,
) -> Response[Union[Box, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        box_id=box_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    box_id: str,
    json_body: BoxUpdate,
) -> Optional[Union[Box, BadRequestError]]:
    """ Update a box """

    return (
        await asyncio_detailed(
            client=client,
            box_id=box_id,
            json_body=json_body,
        )
    ).parsed
