from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.async_task_link import AsyncTaskLink
from ...models.bad_request_error import BadRequestError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    output_processor_id: str,
) -> Dict[str, Any]:
    url = "{}/automation-output-processors/{output_processor_id}:process-output".format(
        client.base_url, output_processor_id=output_processor_id
    )

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    if response.status_code == 202:
        response_202 = AsyncTaskLink.from_dict(response.json())

        return response_202
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[AsyncTaskLink, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    output_processor_id: str,
) -> Response[Union[AsyncTaskLink, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        output_processor_id=output_processor_id,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    output_processor_id: str,
) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    """ Process Output with an Automation Output Processor """

    return sync_detailed(
        client=client,
        output_processor_id=output_processor_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    output_processor_id: str,
) -> Response[Union[AsyncTaskLink, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        output_processor_id=output_processor_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    output_processor_id: str,
) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    """ Process Output with an Automation Output Processor """

    return (
        await asyncio_detailed(
            client=client,
            output_processor_id=output_processor_id,
        )
    ).parsed
