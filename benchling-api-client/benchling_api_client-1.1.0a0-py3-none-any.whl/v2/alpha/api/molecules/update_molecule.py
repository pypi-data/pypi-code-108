from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.molecule import Molecule
from ...models.molecule_update import MoleculeUpdate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    molecule_id: str,
    json_body: MoleculeUpdate,
) -> Dict[str, Any]:
    url = "{}/molecules/{molecule_id}".format(client.base_url, molecule_id=molecule_id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Molecule, BadRequestError]]:
    if response.status_code == 200:
        response_200 = Molecule.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Molecule, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    molecule_id: str,
    json_body: MoleculeUpdate,
) -> Response[Union[Molecule, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        molecule_id=molecule_id,
        json_body=json_body,
    )

    response = httpx.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    molecule_id: str,
    json_body: MoleculeUpdate,
) -> Optional[Union[Molecule, BadRequestError]]:
    """ Update a Molecule """

    return sync_detailed(
        client=client,
        molecule_id=molecule_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    molecule_id: str,
    json_body: MoleculeUpdate,
) -> Response[Union[Molecule, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        molecule_id=molecule_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    molecule_id: str,
    json_body: MoleculeUpdate,
) -> Optional[Union[Molecule, BadRequestError]]:
    """ Update a Molecule """

    return (
        await asyncio_detailed(
            client=client,
            molecule_id=molecule_id,
            json_body=json_body,
        )
    ).parsed
