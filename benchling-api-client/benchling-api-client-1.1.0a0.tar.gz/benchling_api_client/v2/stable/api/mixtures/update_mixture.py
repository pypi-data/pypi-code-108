from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.mixture import Mixture
from ...models.mixture_update import MixtureUpdate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    mixture_id: str,
    json_body: MixtureUpdate,
) -> Dict[str, Any]:
    url = "{}/mixtures/{mixture_id}".format(client.base_url, mixture_id=mixture_id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Mixture, BadRequestError]]:
    if response.status_code == 200:
        response_200 = Mixture.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Mixture, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    mixture_id: str,
    json_body: MixtureUpdate,
) -> Response[Union[Mixture, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        mixture_id=mixture_id,
        json_body=json_body,
    )

    response = httpx.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    mixture_id: str,
    json_body: MixtureUpdate,
) -> Optional[Union[Mixture, BadRequestError]]:
    """Update a mixture.
    To change the parent mixture, set the parent mixture field and specify the desired final state for your ingredients.
    Benchling will recognize that any ingredients you specify that match ingredients on the parent mixture (based on component entity) are inherited. This can be seen on the returned `ingredients[i].hasParent` attribute.
    """

    return sync_detailed(
        client=client,
        mixture_id=mixture_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    mixture_id: str,
    json_body: MixtureUpdate,
) -> Response[Union[Mixture, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        mixture_id=mixture_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    mixture_id: str,
    json_body: MixtureUpdate,
) -> Optional[Union[Mixture, BadRequestError]]:
    """Update a mixture.
    To change the parent mixture, set the parent mixture field and specify the desired final state for your ingredients.
    Benchling will recognize that any ingredients you specify that match ingredients on the parent mixture (based on component entity) are inherited. This can be seen on the returned `ingredients[i].hasParent` attribute.
    """

    return (
        await asyncio_detailed(
            client=client,
            mixture_id=mixture_id,
            json_body=json_body,
        )
    ).parsed
