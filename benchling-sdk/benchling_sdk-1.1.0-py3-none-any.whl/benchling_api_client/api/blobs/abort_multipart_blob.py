from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.empty_object import EmptyObject
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    blob_id: str,
) -> Dict[str, Any]:
    url = "{}/blobs/{blob_id}:abort-upload".format(client.base_url, blob_id=blob_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[EmptyObject, BadRequestError]]:
    if response.status_code == 200:
        response_200 = EmptyObject.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[EmptyObject, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    blob_id: str,
) -> Response[Union[EmptyObject, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        blob_id=blob_id,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    blob_id: str,
) -> Optional[Union[EmptyObject, BadRequestError]]:
    """ Abort multi-part blob upload """

    return sync_detailed(
        client=client,
        blob_id=blob_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    blob_id: str,
) -> Response[Union[EmptyObject, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        blob_id=blob_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    blob_id: str,
) -> Optional[Union[EmptyObject, BadRequestError]]:
    """ Abort multi-part blob upload """

    return (
        await asyncio_detailed(
            client=client,
            blob_id=blob_id,
        )
    ).parsed
