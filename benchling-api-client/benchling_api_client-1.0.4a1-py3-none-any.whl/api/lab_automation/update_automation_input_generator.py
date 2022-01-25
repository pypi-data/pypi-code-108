from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.automation_input_generator import AutomationInputGenerator
from ...models.automation_input_generator_update import AutomationInputGeneratorUpdate
from ...models.bad_request_error import BadRequestError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    input_generator_id: str,
    json_body: AutomationInputGeneratorUpdate,
) -> Dict[str, Any]:
    url = "{}/automation-input-generators/{input_generator_id}".format(
        client.base_url, input_generator_id=input_generator_id
    )

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
) -> Optional[Union[AutomationInputGenerator, BadRequestError]]:
    if response.status_code == 200:
        response_200 = AutomationInputGenerator.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[AutomationInputGenerator, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    input_generator_id: str,
    json_body: AutomationInputGeneratorUpdate,
) -> Response[Union[AutomationInputGenerator, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        input_generator_id=input_generator_id,
        json_body=json_body,
    )

    response = httpx.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    input_generator_id: str,
    json_body: AutomationInputGeneratorUpdate,
) -> Optional[Union[AutomationInputGenerator, BadRequestError]]:
    """ Update an Automation Input Generator """

    return sync_detailed(
        client=client,
        input_generator_id=input_generator_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    input_generator_id: str,
    json_body: AutomationInputGeneratorUpdate,
) -> Response[Union[AutomationInputGenerator, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        input_generator_id=input_generator_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    input_generator_id: str,
    json_body: AutomationInputGeneratorUpdate,
) -> Optional[Union[AutomationInputGenerator, BadRequestError]]:
    """ Update an Automation Input Generator """

    return (
        await asyncio_detailed(
            client=client,
            input_generator_id=input_generator_id,
            json_body=json_body,
        )
    ).parsed
