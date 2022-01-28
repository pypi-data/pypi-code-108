from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.mixture import Mixture
from ...models.mixture_create import MixtureCreate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: MixtureCreate,
) -> Dict[str, Any]:
    url = "{}/mixtures".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Mixture, BadRequestError, None]]:
    if response.status_code == 201:
        response_201 = Mixture.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    if response.status_code == 503:
        response_503 = None

        return response_503
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Mixture, BadRequestError, None]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: MixtureCreate,
) -> Response[Union[Mixture, BadRequestError, None]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    json_body: MixtureCreate,
) -> Optional[Union[Mixture, BadRequestError, None]]:
    """Create a mixture.
    To create a new child mixture (eg. a prep) from a parent mixture (eg. a recipe), set the parent mixture field and specify the desired final state for your ingredients.
    Benchling will recognize that any ingredients you specify that match ingredients on the parent mixture (based on component entity) are inherited. This can be seen on the returned `ingredients[i].hasParent` attribute.
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: MixtureCreate,
) -> Response[Union[Mixture, BadRequestError, None]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    json_body: MixtureCreate,
) -> Optional[Union[Mixture, BadRequestError, None]]:
    """Create a mixture.
    To create a new child mixture (eg. a prep) from a parent mixture (eg. a recipe), set the parent mixture field and specify the desired final state for your ingredients.
    Benchling will recognize that any ingredients you specify that match ingredients on the parent mixture (based on component entity) are inherited. This can be seen on the returned `ingredients[i].hasParent` attribute.
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
