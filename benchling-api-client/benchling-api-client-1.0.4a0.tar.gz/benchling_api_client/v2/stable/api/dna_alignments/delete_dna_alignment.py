from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.empty_object import EmptyObject
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    dna_alignment_id: str,
) -> Dict[str, Any]:
    url = "{}/dna-alignments/{dna_alignment_id}".format(client.base_url, dna_alignment_id=dna_alignment_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[EmptyObject, NotFoundError]]:
    if response.status_code == 200:
        response_200 = EmptyObject.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[EmptyObject, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    dna_alignment_id: str,
) -> Response[Union[EmptyObject, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        dna_alignment_id=dna_alignment_id,
    )

    response = httpx.delete(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    dna_alignment_id: str,
) -> Optional[Union[EmptyObject, NotFoundError]]:
    """ Delete a DNA Alignment """

    return sync_detailed(
        client=client,
        dna_alignment_id=dna_alignment_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    dna_alignment_id: str,
) -> Response[Union[EmptyObject, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        dna_alignment_id=dna_alignment_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.delete(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    dna_alignment_id: str,
) -> Optional[Union[EmptyObject, NotFoundError]]:
    """ Delete a DNA Alignment """

    return (
        await asyncio_detailed(
            client=client,
            dna_alignment_id=dna_alignment_id,
        )
    ).parsed
