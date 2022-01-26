from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.automation_file_inputs_paginated_list import AutomationFileInputsPaginatedList
from ...models.bad_request_error import BadRequestError
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    assay_run_id: str,
    next_token: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/assay-runs/{assay_run_id}/automation-input-generators".format(
        client.base_url, assay_run_id=assay_run_id
    )

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(modified_at, Unset) and modified_at is not None:
        params["modifiedAt"] = modified_at

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[AutomationFileInputsPaginatedList, BadRequestError]]:
    if response.status_code == 200:
        response_200 = AutomationFileInputsPaginatedList.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[AutomationFileInputsPaginatedList, BadRequestError]]:
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
    next_token: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
) -> Response[Union[AutomationFileInputsPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        assay_run_id=assay_run_id,
        next_token=next_token,
        modified_at=modified_at,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    assay_run_id: str,
    next_token: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
) -> Optional[Union[AutomationFileInputsPaginatedList, BadRequestError]]:
    """ list AutomationInputGenerators by Run """

    return sync_detailed(
        client=client,
        assay_run_id=assay_run_id,
        next_token=next_token,
        modified_at=modified_at,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    assay_run_id: str,
    next_token: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
) -> Response[Union[AutomationFileInputsPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        assay_run_id=assay_run_id,
        next_token=next_token,
        modified_at=modified_at,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    assay_run_id: str,
    next_token: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
) -> Optional[Union[AutomationFileInputsPaginatedList, BadRequestError]]:
    """ list AutomationInputGenerators by Run """

    return (
        await asyncio_detailed(
            client=client,
            assay_run_id=assay_run_id,
            next_token=next_token,
            modified_at=modified_at,
        )
    ).parsed
