from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.entry_external_file_by_id import EntryExternalFileById
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    stage_entry_id: str,
    external_file_id: str,
) -> Dict[str, Any]:
    url = "{}/stage-entries/{stage_entry_id}/external-files/{external_file_id}".format(
        client.base_url, stage_entry_id=stage_entry_id, external_file_id=external_file_id
    )

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[EntryExternalFileById]:
    if response.status_code == 200:
        response_200 = EntryExternalFileById.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[EntryExternalFileById]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    stage_entry_id: str,
    external_file_id: str,
) -> Response[EntryExternalFileById]:
    kwargs = _get_kwargs(
        client=client,
        stage_entry_id=stage_entry_id,
        external_file_id=external_file_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    stage_entry_id: str,
    external_file_id: str,
) -> Optional[EntryExternalFileById]:
    """Retrieves the metadata for an external file. Use the 'downloadURL' to download the actual file. (Expand the schema view for details)"""

    return sync_detailed(
        client=client,
        stage_entry_id=stage_entry_id,
        external_file_id=external_file_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    stage_entry_id: str,
    external_file_id: str,
) -> Response[EntryExternalFileById]:
    kwargs = _get_kwargs(
        client=client,
        stage_entry_id=stage_entry_id,
        external_file_id=external_file_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    stage_entry_id: str,
    external_file_id: str,
) -> Optional[EntryExternalFileById]:
    """Retrieves the metadata for an external file. Use the 'downloadURL' to download the actual file. (Expand the schema view for details)"""

    return (
        await asyncio_detailed(
            client=client,
            stage_entry_id=stage_entry_id,
            external_file_id=external_file_id,
        )
    ).parsed
