from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.assay_result import AssayResult
from ...models.bad_request_error import BadRequestError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    assay_result_id: str,
) -> Dict[str, Any]:
    url = "{}/assay-results/{assay_result_id}".format(client.base_url, assay_result_id=assay_result_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[AssayResult, BadRequestError]]:
    if response.status_code == 200:
        response_200 = AssayResult.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[AssayResult, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    assay_result_id: str,
) -> Response[Union[AssayResult, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        assay_result_id=assay_result_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    assay_result_id: str,
) -> Optional[Union[AssayResult, BadRequestError]]:
    """ Get a result """

    return sync_detailed(
        client=client,
        assay_result_id=assay_result_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    assay_result_id: str,
) -> Response[Union[AssayResult, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        assay_result_id=assay_result_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    assay_result_id: str,
) -> Optional[Union[AssayResult, BadRequestError]]:
    """ Get a result """

    return (
        await asyncio_detailed(
            client=client,
            assay_result_id=assay_result_id,
        )
    ).parsed
