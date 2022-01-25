from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.deprecated_automation_output_processors_paginated_list import (
    DeprecatedAutomationOutputProcessorsPaginatedList,
)
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    assay_run_id: str,
    next_token: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/assay-runs/{assay_run_id}/automation-output-processors".format(
        client.base_url, assay_run_id=assay_run_id
    )

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[DeprecatedAutomationOutputProcessorsPaginatedList, BadRequestError]]:
    if response.status_code == 200:
        response_200 = DeprecatedAutomationOutputProcessorsPaginatedList.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[DeprecatedAutomationOutputProcessorsPaginatedList, BadRequestError]]:
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
) -> Response[Union[DeprecatedAutomationOutputProcessorsPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        assay_run_id=assay_run_id,
        next_token=next_token,
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
) -> Optional[Union[DeprecatedAutomationOutputProcessorsPaginatedList, BadRequestError]]:
    """ Deprecated in favor of '/automation-output-processors'. For each output config in the run config, will create an empty automationOutputProcessor for the run if one doesn't exist. """

    return sync_detailed(
        client=client,
        assay_run_id=assay_run_id,
        next_token=next_token,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    assay_run_id: str,
    next_token: Union[Unset, str] = UNSET,
) -> Response[Union[DeprecatedAutomationOutputProcessorsPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        assay_run_id=assay_run_id,
        next_token=next_token,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    assay_run_id: str,
    next_token: Union[Unset, str] = UNSET,
) -> Optional[Union[DeprecatedAutomationOutputProcessorsPaginatedList, BadRequestError]]:
    """ Deprecated in favor of '/automation-output-processors'. For each output config in the run config, will create an empty automationOutputProcessor for the run if one doesn't exist. """

    return (
        await asyncio_detailed(
            client=client,
            assay_run_id=assay_run_id,
            next_token=next_token,
        )
    ).parsed
