from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import Client
from ...models.en_data_point_existence_dto import EnDataPointExistenceDTO
from ...models.en_data_point_type import EnDataPointType
from ...models.problem_details import ProblemDetails
from ...types import UNSET, Response, Unset


def _get_kwargs(
    tenant_name: Optional[str],
    *,
    client: Client,
    filter_tags: Union[Unset, None, List[str]] = UNSET,
    type: Union[Unset, None, List[EnDataPointType]] = UNSET,
    existence: Union[Unset, None, List[EnDataPointExistenceDTO]] = UNSET,
) -> Dict[str, Any]:
    url = "{}/DataPoint/tenant/{tenantName}/tags".format(client.base_url, tenantName=tenant_name)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    json_filter_tags: Union[Unset, None, List[str]] = UNSET
    if not isinstance(filter_tags, Unset):
        if filter_tags is None:
            json_filter_tags = None
        else:
            json_filter_tags = filter_tags

    json_type: Union[Unset, None, List[str]] = UNSET
    if not isinstance(type, Unset):
        if type is None:
            json_type = None
        else:
            json_type = []
            for type_item_data in type:
                type_item = type_item_data.value

                json_type.append(type_item)

    json_existence: Union[Unset, None, List[str]] = UNSET
    if not isinstance(existence, Unset):
        if existence is None:
            json_existence = None
        else:
            json_existence = []
            for existence_item_data in existence:
                existence_item = existence_item_data.value

                json_existence.append(existence_item)

    params: Dict[str, Any] = {
        "filterTags": json_filter_tags,
        "type": json_type,
        "existence": json_existence,
    }
    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[List[str], ProblemDetails]]:
    if response.status_code == 200:
        response_200 = cast(List[str], response.json())

        return response_200
    if response.status_code == 401:
        response_401 = ProblemDetails.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = ProblemDetails.from_dict(response.json())

        return response_403
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[List[str], ProblemDetails]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    tenant_name: Optional[str],
    *,
    client: Client,
    filter_tags: Union[Unset, None, List[str]] = UNSET,
    type: Union[Unset, None, List[EnDataPointType]] = UNSET,
    existence: Union[Unset, None, List[EnDataPointExistenceDTO]] = UNSET,
) -> Response[Union[List[str], ProblemDetails]]:
    kwargs = _get_kwargs(
        tenant_name=tenant_name,
        client=client,
        filter_tags=filter_tags,
        type=type,
        existence=existence,
    )

    response = httpx.get(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    tenant_name: Optional[str],
    *,
    client: Client,
    filter_tags: Union[Unset, None, List[str]] = UNSET,
    type: Union[Unset, None, List[EnDataPointType]] = UNSET,
    existence: Union[Unset, None, List[EnDataPointExistenceDTO]] = UNSET,
) -> Optional[Union[List[str], ProblemDetails]]:
    """ """

    return sync_detailed(
        tenant_name=tenant_name,
        client=client,
        filter_tags=filter_tags,
        type=type,
        existence=existence,
    ).parsed


async def asyncio_detailed(
    tenant_name: Optional[str],
    *,
    client: Client,
    filter_tags: Union[Unset, None, List[str]] = UNSET,
    type: Union[Unset, None, List[EnDataPointType]] = UNSET,
    existence: Union[Unset, None, List[EnDataPointExistenceDTO]] = UNSET,
) -> Response[Union[List[str], ProblemDetails]]:
    kwargs = _get_kwargs(
        tenant_name=tenant_name,
        client=client,
        filter_tags=filter_tags,
        type=type,
        existence=existence,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    tenant_name: Optional[str],
    *,
    client: Client,
    filter_tags: Union[Unset, None, List[str]] = UNSET,
    type: Union[Unset, None, List[EnDataPointType]] = UNSET,
    existence: Union[Unset, None, List[EnDataPointExistenceDTO]] = UNSET,
) -> Optional[Union[List[str], ProblemDetails]]:
    """ """

    return (
        await asyncio_detailed(
            tenant_name=tenant_name,
            client=client,
            filter_tags=filter_tags,
            type=type,
            existence=existence,
        )
    ).parsed
