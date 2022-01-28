from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.rna_oligos_archival_change import RnaOligosArchivalChange
from ...models.rna_oligos_archive import RnaOligosArchive
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: RnaOligosArchive,
) -> Dict[str, Any]:
    url = "{}/rna-oligos:archive".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[RnaOligosArchivalChange, BadRequestError]]:
    if response.status_code == 200:
        response_200 = RnaOligosArchivalChange.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[RnaOligosArchivalChange, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: RnaOligosArchive,
) -> Response[Union[RnaOligosArchivalChange, BadRequestError]]:
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
    json_body: RnaOligosArchive,
) -> Optional[Union[RnaOligosArchivalChange, BadRequestError]]:
    """ Archive RNA Oligos """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: RnaOligosArchive,
) -> Response[Union[RnaOligosArchivalChange, BadRequestError]]:
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
    json_body: RnaOligosArchive,
) -> Optional[Union[RnaOligosArchivalChange, BadRequestError]]:
    """ Archive RNA Oligos """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
