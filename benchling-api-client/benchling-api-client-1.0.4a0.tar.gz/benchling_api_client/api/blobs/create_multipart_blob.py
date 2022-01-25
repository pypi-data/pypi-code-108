from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.blob import Blob
from ...models.blob_multipart_create import BlobMultipartCreate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    json_body: BlobMultipartCreate,
) -> Dict[str, Any]:
    url = "{}/blobs:start-multipart-upload".format(client.base_url)

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
    json_body: BlobMultipartCreate,
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
    json_body: BlobMultipartCreate,
) -> Optional[Union[Blob, BadRequestError]]:
    """
    Blobs may be uploaded using multi-part upload. This endpoint initiates the upload process - blob parts can then be uploaded in multiple blob parts.

    ## Multipart Upload

    If a blob is larger than 10MB, it should be uploaded in multiple parts using the following endpoints:
    - [Start a multi-part blob upload](#/Blobs/createMultipartBlob)
    - [Upload a blob part](#/Blobs/createBlobPart)
    - [Complete a blob upload](#/Blobs/completeMultipartBlob)

    Each part must be at least 5MB in size, except for the last part. We recommend keeping each part to under 10MB when uploading.

    Each part has a *partNumber* and an *eTag*. The part number can be any number between 1 to 10,000, inclusive - this number should be unique and identifies the order of the part in the final blob. The eTag of a part is returned in the API response - this eTag must be specified when completing the upload in order to ensure the server has received all the expected parts.
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: BlobMultipartCreate,
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
    json_body: BlobMultipartCreate,
) -> Optional[Union[Blob, BadRequestError]]:
    """
    Blobs may be uploaded using multi-part upload. This endpoint initiates the upload process - blob parts can then be uploaded in multiple blob parts.

    ## Multipart Upload

    If a blob is larger than 10MB, it should be uploaded in multiple parts using the following endpoints:
    - [Start a multi-part blob upload](#/Blobs/createMultipartBlob)
    - [Upload a blob part](#/Blobs/createBlobPart)
    - [Complete a blob upload](#/Blobs/completeMultipartBlob)

    Each part must be at least 5MB in size, except for the last part. We recommend keeping each part to under 10MB when uploading.

    Each part has a *partNumber* and an *eTag*. The part number can be any number between 1 to 10,000, inclusive - this number should be unique and identifies the order of the part in the final blob. The eTag of a part is returned in the API response - this eTag must be specified when completing the upload in order to ensure the server has received all the expected parts.
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
