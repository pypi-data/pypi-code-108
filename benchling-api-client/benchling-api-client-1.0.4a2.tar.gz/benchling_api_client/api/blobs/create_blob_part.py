from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.blob_part import BlobPart
from ...models.blob_part_create import BlobPartCreate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    blob_id: str,
    json_body: BlobPartCreate,
) -> Dict[str, Any]:
    url = "{}/blobs/{blob_id}/parts".format(client.base_url, blob_id=blob_id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[BlobPart, BadRequestError]]:
    if response.status_code == 200:
        response_200 = BlobPart.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[BlobPart, BadRequestError]]:
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
    json_body: BlobPartCreate,
) -> Response[Union[BlobPart, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        blob_id=blob_id,
        json_body=json_body,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    blob_id: str,
    json_body: BlobPartCreate,
) -> Optional[Union[BlobPart, BadRequestError]]:
    """
    Upload a part of the blob. This part must be at least 5MB, unless it's the last or only part. It's recommended to keep the part size around 10MB.

    The data64 parameter is the base64-encoded part contents, and the md5 parameter is the hex-encoded MD5 hash of the part contents. For example, given the string hello, data64 is aGVsbG8= and md5 is 5d41402abc4b2a76b9719d911017c592.

    ## Multipart Upload

    If a blob is larger than 10MB, it should be uploaded in multiple parts using the following endpoints:
    - [Start a multi-part blob upload](#/Blobs/createMultipartBlob)
    - [Upload a blob part](#/Blobs/createBlobPart)
    - [Complete a blob upload](#/Blobs/completeMultipartBlob)

    Each part has a *partNumber* and an *eTag*. The part number can be any number between 1 to 10,000, inclusive - this number should be unique and identifies the order of the part in the final blob. The eTag of a part is returned in the API response - this eTag must be specified when completing the upload in order to ensure the server has received all the expected parts.
    """

    return sync_detailed(
        client=client,
        blob_id=blob_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    blob_id: str,
    json_body: BlobPartCreate,
) -> Response[Union[BlobPart, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        blob_id=blob_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    blob_id: str,
    json_body: BlobPartCreate,
) -> Optional[Union[BlobPart, BadRequestError]]:
    """
    Upload a part of the blob. This part must be at least 5MB, unless it's the last or only part. It's recommended to keep the part size around 10MB.

    The data64 parameter is the base64-encoded part contents, and the md5 parameter is the hex-encoded MD5 hash of the part contents. For example, given the string hello, data64 is aGVsbG8= and md5 is 5d41402abc4b2a76b9719d911017c592.

    ## Multipart Upload

    If a blob is larger than 10MB, it should be uploaded in multiple parts using the following endpoints:
    - [Start a multi-part blob upload](#/Blobs/createMultipartBlob)
    - [Upload a blob part](#/Blobs/createBlobPart)
    - [Complete a blob upload](#/Blobs/completeMultipartBlob)

    Each part has a *partNumber* and an *eTag*. The part number can be any number between 1 to 10,000, inclusive - this number should be unique and identifies the order of the part in the final blob. The eTag of a part is returned in the API response - this eTag must be specified when completing the upload in order to ensure the server has received all the expected parts.
    """

    return (
        await asyncio_detailed(
            client=client,
            blob_id=blob_id,
            json_body=json_body,
        )
    ).parsed
