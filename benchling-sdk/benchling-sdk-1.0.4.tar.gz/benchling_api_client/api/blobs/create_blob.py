from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.blob import Blob
from ...models.blob_create import BlobCreate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: BlobCreate,
) -> Dict[str, Any]:
    url = "{}/blobs".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Blob, BadRequestError]]:
    if response.status_code == 200:
        response_200 = Blob.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Blob, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: BlobCreate,
) -> Response[Union[Blob, BadRequestError]]:
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
    json_body: BlobCreate,
) -> Optional[Union[Blob, BadRequestError]]:
    """
    This endpoint uploads a blob in a single API call.

    Blobs larger than 10MB should be uploaded in [multiple parts](#/Blobs/createMultipartBlob). The data64 parameter is the base64-encoded part contents, and the md5 parameter is the hex-encoded MD5 hash of the part contents. For example, given the string hello, data64 is aGVsbG8= and md5 is 5d41402abc4b2a76b9719d911017c592.
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: BlobCreate,
) -> Response[Union[Blob, BadRequestError]]:
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
    json_body: BlobCreate,
) -> Optional[Union[Blob, BadRequestError]]:
    """
    This endpoint uploads a blob in a single API call.

    Blobs larger than 10MB should be uploaded in [multiple parts](#/Blobs/createMultipartBlob). The data64 parameter is the base64-encoded part contents, and the md5 parameter is the hex-encoded MD5 hash of the part contents. For example, given the string hello, data64 is aGVsbG8= and md5 is 5d41402abc4b2a76b9719d911017c592.
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
