from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.file_upload_file_multipart_data import FileUploadFileMultipartData
from ...models.problem_details import ProblemDetails
from ...types import Response


def _get_kwargs(
    file_id: str,
    *,
    client: Client,
    multipart_data: FileUploadFileMultipartData,
) -> Dict[str, Any]:
    url = "{}/File/{fileId}".format(client.base_url, fileId=file_id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    multipart_multipart_data = multipart_data.to_multipart()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "files": multipart_multipart_data,
    }


def _parse_response(*, response: httpx.Response) -> Optional[ProblemDetails]:
    if response.status_code == 401:
        response_401 = ProblemDetails.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = ProblemDetails.from_dict(response.json())

        return response_403
    return None


def _build_response(*, response: httpx.Response) -> Response[ProblemDetails]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    file_id: str,
    *,
    client: Client,
    multipart_data: FileUploadFileMultipartData,
) -> Response[ProblemDetails]:
    kwargs = _get_kwargs(
        file_id=file_id,
        client=client,
        multipart_data=multipart_data,
    )

    response = httpx.put(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    file_id: str,
    *,
    client: Client,
    multipart_data: FileUploadFileMultipartData,
) -> Optional[ProblemDetails]:
    """ """

    return sync_detailed(
        file_id=file_id,
        client=client,
        multipart_data=multipart_data,
    ).parsed


async def asyncio_detailed(
    file_id: str,
    *,
    client: Client,
    multipart_data: FileUploadFileMultipartData,
) -> Response[ProblemDetails]:
    kwargs = _get_kwargs(
        file_id=file_id,
        client=client,
        multipart_data=multipart_data,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.put(**kwargs)

    return _build_response(response=response)


async def asyncio(
    file_id: str,
    *,
    client: Client,
    multipart_data: FileUploadFileMultipartData,
) -> Optional[ProblemDetails]:
    """ """

    return (
        await asyncio_detailed(
            file_id=file_id,
            client=client,
            multipart_data=multipart_data,
        )
    ).parsed
