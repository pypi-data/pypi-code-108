from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.not_found_error import NotFoundError
from ...models.user import User
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    user_id: str,
) -> Dict[str, Any]:
    url = "{}/users/{user_id}".format(client.base_url, user_id=user_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[User, NotFoundError]]:
    if response.status_code == 200:
        response_200 = User.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[User, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    user_id: str,
) -> Response[Union[User, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        user_id=user_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    user_id: str,
) -> Optional[Union[User, NotFoundError]]:
    """Returns a user by ID if the caller has permission to view. The following roles have view permission:
    - tenant admins
    - members of any of the user's organizations
    """

    return sync_detailed(
        client=client,
        user_id=user_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    user_id: str,
) -> Response[Union[User, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        user_id=user_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    user_id: str,
) -> Optional[Union[User, NotFoundError]]:
    """Returns a user by ID if the caller has permission to view. The following roles have view permission:
    - tenant admins
    - members of any of the user's organizations
    """

    return (
        await asyncio_detailed(
            client=client,
            user_id=user_id,
        )
    ).parsed
