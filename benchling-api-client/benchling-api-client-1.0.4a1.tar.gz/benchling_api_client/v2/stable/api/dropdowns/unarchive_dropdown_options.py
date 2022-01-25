from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.dropdown_options_archival_change import DropdownOptionsArchivalChange
from ...models.dropdown_options_unarchive import DropdownOptionsUnarchive
from ...models.forbidden_error import ForbiddenError
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    dropdown_id: str,
    json_body: DropdownOptionsUnarchive,
) -> Dict[str, Any]:
    url = "{}/dropdowns/{dropdown_id}/options:unarchive".format(client.base_url, dropdown_id=dropdown_id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[DropdownOptionsArchivalChange, BadRequestError, ForbiddenError, NotFoundError]]:
    if response.status_code == 200:
        response_200 = DropdownOptionsArchivalChange.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    if response.status_code == 403:
        response_403 = ForbiddenError.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[DropdownOptionsArchivalChange, BadRequestError, ForbiddenError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    dropdown_id: str,
    json_body: DropdownOptionsUnarchive,
) -> Response[Union[DropdownOptionsArchivalChange, BadRequestError, ForbiddenError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        dropdown_id=dropdown_id,
        json_body=json_body,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    dropdown_id: str,
    json_body: DropdownOptionsUnarchive,
) -> Optional[Union[DropdownOptionsArchivalChange, BadRequestError, ForbiddenError, NotFoundError]]:
    """ Unarchive options belonging to a dropdown """

    return sync_detailed(
        client=client,
        dropdown_id=dropdown_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    dropdown_id: str,
    json_body: DropdownOptionsUnarchive,
) -> Response[Union[DropdownOptionsArchivalChange, BadRequestError, ForbiddenError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        dropdown_id=dropdown_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    dropdown_id: str,
    json_body: DropdownOptionsUnarchive,
) -> Optional[Union[DropdownOptionsArchivalChange, BadRequestError, ForbiddenError, NotFoundError]]:
    """ Unarchive options belonging to a dropdown """

    return (
        await asyncio_detailed(
            client=client,
            dropdown_id=dropdown_id,
            json_body=json_body,
        )
    ).parsed
