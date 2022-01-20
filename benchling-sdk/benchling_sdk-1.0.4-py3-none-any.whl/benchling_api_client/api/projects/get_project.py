from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.not_found_error import NotFoundError
from ...models.project import Project
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    project_id: str,
) -> Dict[str, Any]:
    url = "{}/projects/{project_id}".format(client.base_url, project_id=project_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Project, NotFoundError]]:
    if response.status_code == 200:
        response_200 = Project.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Project, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    project_id: str,
) -> Response[Union[Project, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        project_id=project_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    project_id: str,
) -> Optional[Union[Project, NotFoundError]]:
    """ Get a project by ID """

    return sync_detailed(
        client=client,
        project_id=project_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    project_id: str,
) -> Response[Union[Project, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        project_id=project_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    project_id: str,
) -> Optional[Union[Project, NotFoundError]]:
    """ Get a project by ID """

    return (
        await asyncio_detailed(
            client=client,
            project_id=project_id,
        )
    ).parsed
