from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.assay_result_ids_response import AssayResultIdsResponse
from ...models.assay_results_archive import AssayResultsArchive
from ...models.bad_request_error import BadRequestError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: AssayResultsArchive,
) -> Dict[str, Any]:
    url = "{}/assay-results:archive".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[AssayResultIdsResponse, BadRequestError]]:
    if response.status_code == 200:
        response_200 = AssayResultIdsResponse.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[AssayResultIdsResponse, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: AssayResultsArchive,
) -> Response[Union[AssayResultIdsResponse, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    json_body: AssayResultsArchive,
) -> Optional[Union[AssayResultIdsResponse, BadRequestError]]:
    """**Only results that have not been added to a Notebook Entry can be Archived.**
    Once results are attached to a notebook entry, they are tracked in the history of that notebook entry, and cannot be archived.
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: AssayResultsArchive,
) -> Response[Union[AssayResultIdsResponse, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    json_body: AssayResultsArchive,
) -> Optional[Union[AssayResultIdsResponse, BadRequestError]]:
    """**Only results that have not been added to a Notebook Entry can be Archived.**
    Once results are attached to a notebook entry, they are tracked in the history of that notebook entry, and cannot be archived.
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
