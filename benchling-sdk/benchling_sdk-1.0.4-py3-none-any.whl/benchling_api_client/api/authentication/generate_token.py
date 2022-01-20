from typing import Any, Dict, Optional, Union

from attr import asdict
import httpx

from ...client import AuthenticatedClient
from ...models.o_auth_bad_request_error import OAuthBadRequestError
from ...models.o_auth_unauthorized_error import OAuthUnauthorizedError
from ...models.token_create import TokenCreate
from ...models.token_response import TokenResponse
from ...types import Response


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    form_data: TokenCreate,
) -> Dict[str, Any]:
    url = "{}/token".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "data": asdict(form_data),
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[TokenResponse, OAuthBadRequestError, OAuthUnauthorizedError]]:
    if response.status_code == 200:
        response_200 = TokenResponse.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = OAuthBadRequestError.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = OAuthUnauthorizedError.from_dict(response.json())

        return response_401
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[TokenResponse, OAuthBadRequestError, OAuthUnauthorizedError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    form_data: TokenCreate,
) -> Response[Union[TokenResponse, OAuthBadRequestError, OAuthUnauthorizedError]]:
    kwargs = _get_kwargs(
        client=client,
        form_data=form_data,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    form_data: TokenCreate,
) -> Optional[Union[TokenResponse, OAuthBadRequestError, OAuthUnauthorizedError]]:
    """ Generate a token """

    return sync_detailed(
        client=client,
        form_data=form_data,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    form_data: TokenCreate,
) -> Response[Union[TokenResponse, OAuthBadRequestError, OAuthUnauthorizedError]]:
    kwargs = _get_kwargs(
        client=client,
        form_data=form_data,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    form_data: TokenCreate,
) -> Optional[Union[TokenResponse, OAuthBadRequestError, OAuthUnauthorizedError]]:
    """ Generate a token """

    return (
        await asyncio_detailed(
            client=client,
            form_data=form_data,
        )
    ).parsed
