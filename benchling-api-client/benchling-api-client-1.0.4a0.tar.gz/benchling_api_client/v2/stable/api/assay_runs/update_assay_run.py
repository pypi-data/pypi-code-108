from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.assay_run import AssayRun
from ...models.assay_run_update import AssayRunUpdate
from ...models.bad_request_error import BadRequestError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    assay_run_id: str,
    json_body: AssayRunUpdate,
) -> Dict[str, Any]:
    url = "{}/assay-runs/{assay_run_id}".format(client.base_url, assay_run_id=assay_run_id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[AssayRun, BadRequestError]]:
    if response.status_code == 200:
        response_200 = AssayRun.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[AssayRun, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    assay_run_id: str,
    json_body: AssayRunUpdate,
) -> Response[Union[AssayRun, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        assay_run_id=assay_run_id,
        json_body=json_body,
    )

    response = httpx.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    assay_run_id: str,
    json_body: AssayRunUpdate,
) -> Optional[Union[AssayRun, BadRequestError]]:
    """ Update a run """

    return sync_detailed(
        client=client,
        assay_run_id=assay_run_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    assay_run_id: str,
    json_body: AssayRunUpdate,
) -> Response[Union[AssayRun, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        assay_run_id=assay_run_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    assay_run_id: str,
    json_body: AssayRunUpdate,
) -> Optional[Union[AssayRun, BadRequestError]]:
    """ Update a run """

    return (
        await asyncio_detailed(
            client=client,
            assay_run_id=assay_run_id,
            json_body=json_body,
        )
    ).parsed
