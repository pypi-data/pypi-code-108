from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.batches_bulk_get import BatchesBulkGet
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    batch_ids: Union[Unset, str] = UNSET,
    batch_names: Union[Unset, str] = UNSET,
    registry_id: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/batches:bulk-get".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if not isinstance(batch_ids, Unset) and batch_ids is not None:
        params["batchIds"] = batch_ids
    if not isinstance(batch_names, Unset) and batch_names is not None:
        params["batchNames"] = batch_names
    if not isinstance(registry_id, Unset) and registry_id is not None:
        params["registryId"] = registry_id

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[BatchesBulkGet, BadRequestError]]:
    if response.status_code == 200:
        response_200 = BatchesBulkGet.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[BatchesBulkGet, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    batch_ids: Union[Unset, str] = UNSET,
    batch_names: Union[Unset, str] = UNSET,
    registry_id: Union[Unset, str] = UNSET,
) -> Response[Union[BatchesBulkGet, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        batch_ids=batch_ids,
        batch_names=batch_names,
        registry_id=registry_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    batch_ids: Union[Unset, str] = UNSET,
    batch_names: Union[Unset, str] = UNSET,
    registry_id: Union[Unset, str] = UNSET,
) -> Optional[Union[BatchesBulkGet, BadRequestError]]:
    """Batches can be queried by their IDs or their names. Querying by name requires specifying a registryId since batch names are not necessarily unique across registries. Batches must be registered to query by name."""

    return sync_detailed(
        client=client,
        batch_ids=batch_ids,
        batch_names=batch_names,
        registry_id=registry_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    batch_ids: Union[Unset, str] = UNSET,
    batch_names: Union[Unset, str] = UNSET,
    registry_id: Union[Unset, str] = UNSET,
) -> Response[Union[BatchesBulkGet, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        batch_ids=batch_ids,
        batch_names=batch_names,
        registry_id=registry_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    batch_ids: Union[Unset, str] = UNSET,
    batch_names: Union[Unset, str] = UNSET,
    registry_id: Union[Unset, str] = UNSET,
) -> Optional[Union[BatchesBulkGet, BadRequestError]]:
    """Batches can be queried by their IDs or their names. Querying by name requires specifying a registryId since batch names are not necessarily unique across registries. Batches must be registered to query by name."""

    return (
        await asyncio_detailed(
            client=client,
            batch_ids=batch_ids,
            batch_names=batch_names,
            registry_id=registry_id,
        )
    ).parsed
