import datetime
from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.assay_results_paginated_list import AssayResultsPaginatedList
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    schema_id: str,
    min_created_time: Union[Unset, datetime.datetime] = UNSET,
    max_created_time: Union[Unset, datetime.datetime] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    entity_ids: Union[Unset, str] = UNSET,
    storage_ids: Union[Unset, str] = UNSET,
    assay_run_ids: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/assay-results".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_min_created_time: Union[Unset, str] = UNSET
    if not isinstance(min_created_time, Unset):
        json_min_created_time = min_created_time.isoformat()

    json_max_created_time: Union[Unset, str] = UNSET
    if not isinstance(max_created_time, Unset):
        json_max_created_time = max_created_time.isoformat()

    params: Dict[str, Any] = {
        "schemaId": schema_id,
    }
    if not isinstance(json_min_created_time, Unset) and json_min_created_time is not None:
        params["minCreatedTime"] = json_min_created_time
    if not isinstance(json_max_created_time, Unset) and json_max_created_time is not None:
        params["maxCreatedTime"] = json_max_created_time
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size
    if not isinstance(entity_ids, Unset) and entity_ids is not None:
        params["entityIds"] = entity_ids
    if not isinstance(storage_ids, Unset) and storage_ids is not None:
        params["storageIds"] = storage_ids
    if not isinstance(assay_run_ids, Unset) and assay_run_ids is not None:
        params["assayRunIds"] = assay_run_ids
    if not isinstance(ids, Unset) and ids is not None:
        params["ids"] = ids

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[AssayResultsPaginatedList]:
    if response.status_code == 200:
        response_200 = AssayResultsPaginatedList.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[AssayResultsPaginatedList]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    schema_id: str,
    min_created_time: Union[Unset, datetime.datetime] = UNSET,
    max_created_time: Union[Unset, datetime.datetime] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    entity_ids: Union[Unset, str] = UNSET,
    storage_ids: Union[Unset, str] = UNSET,
    assay_run_ids: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
) -> Response[AssayResultsPaginatedList]:
    kwargs = _get_kwargs(
        client=client,
        schema_id=schema_id,
        min_created_time=min_created_time,
        max_created_time=max_created_time,
        next_token=next_token,
        page_size=page_size,
        entity_ids=entity_ids,
        storage_ids=storage_ids,
        assay_run_ids=assay_run_ids,
        ids=ids,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    schema_id: str,
    min_created_time: Union[Unset, datetime.datetime] = UNSET,
    max_created_time: Union[Unset, datetime.datetime] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    entity_ids: Union[Unset, str] = UNSET,
    storage_ids: Union[Unset, str] = UNSET,
    assay_run_ids: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
) -> Optional[AssayResultsPaginatedList]:
    """ List results """

    return sync_detailed(
        client=client,
        schema_id=schema_id,
        min_created_time=min_created_time,
        max_created_time=max_created_time,
        next_token=next_token,
        page_size=page_size,
        entity_ids=entity_ids,
        storage_ids=storage_ids,
        assay_run_ids=assay_run_ids,
        ids=ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    schema_id: str,
    min_created_time: Union[Unset, datetime.datetime] = UNSET,
    max_created_time: Union[Unset, datetime.datetime] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    entity_ids: Union[Unset, str] = UNSET,
    storage_ids: Union[Unset, str] = UNSET,
    assay_run_ids: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
) -> Response[AssayResultsPaginatedList]:
    kwargs = _get_kwargs(
        client=client,
        schema_id=schema_id,
        min_created_time=min_created_time,
        max_created_time=max_created_time,
        next_token=next_token,
        page_size=page_size,
        entity_ids=entity_ids,
        storage_ids=storage_ids,
        assay_run_ids=assay_run_ids,
        ids=ids,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    schema_id: str,
    min_created_time: Union[Unset, datetime.datetime] = UNSET,
    max_created_time: Union[Unset, datetime.datetime] = UNSET,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    entity_ids: Union[Unset, str] = UNSET,
    storage_ids: Union[Unset, str] = UNSET,
    assay_run_ids: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
) -> Optional[AssayResultsPaginatedList]:
    """ List results """

    return (
        await asyncio_detailed(
            client=client,
            schema_id=schema_id,
            min_created_time=min_created_time,
            max_created_time=max_created_time,
            next_token=next_token,
            page_size=page_size,
            entity_ids=entity_ids,
            storage_ids=storage_ids,
            assay_run_ids=assay_run_ids,
            ids=ids,
        )
    ).parsed
