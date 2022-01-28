from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.async_task_link import AsyncTaskLink
from ...models.bad_request_error import BadRequestError
from ...models.registry_bulk_upsert_objects_request import RegistryBulkUpsertObjectsRequest
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    registry_id: str,
    json_body: RegistryBulkUpsertObjectsRequest,
) -> Dict[str, Any]:
    url = "{}/registries/{registry_id}:bulk-upsert".format(client.base_url, registry_id=registry_id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
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
    registry_id: str,
    json_body: RegistryBulkUpsertObjectsRequest,
) -> Response[Union[AsyncTaskLink, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        registry_id=registry_id,
        json_body=json_body,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    registry_id: str,
    json_body: RegistryBulkUpsertObjectsRequest,
) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    """Currently supported object types: custom entities.

    This operation performs the following actions:
    1. Any existing objects are looked up in Benchling by the provided entity registry ID.
    2. Then, all objects are either created or updated accordingly, temporarily skipping any schema field links between objects.
    3. Schema field links between objects are populated according to the provided identifier. In the `value` field of the [Field](#/components/schemas/FieldWithResolution) resource, the entity registry ID, name, or alias may be provided instead of the API ID if desired. You may link to objects being created in the same operation.
    4. Entities are registered, using the provided name and entity registry ID.

    If any action fails, the whole operation is canceled and no objects are created or updated.
    """

    return sync_detailed(
        client=client,
        registry_id=registry_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    registry_id: str,
    json_body: RegistryBulkUpsertObjectsRequest,
) -> Response[Union[AsyncTaskLink, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        registry_id=registry_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    registry_id: str,
    json_body: RegistryBulkUpsertObjectsRequest,
) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    """Currently supported object types: custom entities.

    This operation performs the following actions:
    1. Any existing objects are looked up in Benchling by the provided entity registry ID.
    2. Then, all objects are either created or updated accordingly, temporarily skipping any schema field links between objects.
    3. Schema field links between objects are populated according to the provided identifier. In the `value` field of the [Field](#/components/schemas/FieldWithResolution) resource, the entity registry ID, name, or alias may be provided instead of the API ID if desired. You may link to objects being created in the same operation.
    4. Entities are registered, using the provided name and entity registry ID.

    If any action fails, the whole operation is canceled and no objects are created or updated.
    """

    return (
        await asyncio_detailed(
            client=client,
            registry_id=registry_id,
            json_body=json_body,
        )
    ).parsed
