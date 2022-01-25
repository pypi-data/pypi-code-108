from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.not_found_error import NotFoundError
from ...models.organization import Organization
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    organization_id: str,
) -> Dict[str, Any]:
    url = "{}/organizations/{organization_id}".format(client.base_url, organization_id=organization_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Organization, NotFoundError]]:
    if response.status_code == 200:
        response_200 = Organization.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Organization, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    organization_id: str,
) -> Response[Union[Organization, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        organization_id=organization_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    organization_id: str,
) -> Optional[Union[Organization, NotFoundError]]:
    """Returns an organization by ID if the caller has permission to view. The following roles have view permission:
    - tenant admins
    - members of the organization
    """

    return sync_detailed(
        client=client,
        organization_id=organization_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    organization_id: str,
) -> Response[Union[Organization, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        organization_id=organization_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    organization_id: str,
) -> Optional[Union[Organization, NotFoundError]]:
    """Returns an organization by ID if the caller has permission to view. The following roles have view permission:
    - tenant admins
    - members of the organization
    """

    return (
        await asyncio_detailed(
            client=client,
            organization_id=organization_id,
        )
    ).parsed
