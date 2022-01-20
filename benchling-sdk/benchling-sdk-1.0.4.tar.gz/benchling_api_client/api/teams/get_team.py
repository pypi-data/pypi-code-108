from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.not_found_error import NotFoundError
from ...models.team import Team
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    team_id: str,
) -> Dict[str, Any]:
    url = "{}/teams/{team_id}".format(client.base_url, team_id=team_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Team, NotFoundError]]:
    if response.status_code == 200:
        response_200 = Team.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Team, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    team_id: str,
) -> Response[Union[Team, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        team_id=team_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    team_id: str,
) -> Optional[Union[Team, NotFoundError]]:
    """Returns a team by ID if the caller has permission to view. The following roles have view permission:
    - tenant admins
    - members of the team's organization
    """

    return sync_detailed(
        client=client,
        team_id=team_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    team_id: str,
) -> Response[Union[Team, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        team_id=team_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    team_id: str,
) -> Optional[Union[Team, NotFoundError]]:
    """Returns a team by ID if the caller has permission to view. The following roles have view permission:
    - tenant admins
    - members of the team's organization
    """

    return (
        await asyncio_detailed(
            client=client,
            team_id=team_id,
        )
    ).parsed
