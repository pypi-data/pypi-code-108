from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.transform import Transform
from ...models.transform_patch import TransformPatch
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    transform_id: str,
    json_body: TransformPatch,
) -> Dict[str, Any]:
    url = "{}/v2/automation-file-transforms/{transform_id}".format(client.base_url, transform_id=transform_id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Transform, BadRequestError]]:
    if response.status_code == 200:
        response_200 = Transform.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Transform, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    transform_id: str,
    json_body: TransformPatch,
) -> Response[Union[Transform, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        transform_id=transform_id,
        json_body=json_body,
    )

    response = httpx.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    transform_id: str,
    json_body: TransformPatch,
) -> Optional[Union[Transform, BadRequestError]]:
    """ Update a Lab Automation Transform step """

    return sync_detailed(
        client=client,
        transform_id=transform_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    transform_id: str,
    json_body: TransformPatch,
) -> Response[Union[Transform, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        transform_id=transform_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    transform_id: str,
    json_body: TransformPatch,
) -> Optional[Union[Transform, BadRequestError]]:
    """ Update a Lab Automation Transform step """

    return (
        await asyncio_detailed(
            client=client,
            transform_id=transform_id,
            json_body=json_body,
        )
    ).parsed
