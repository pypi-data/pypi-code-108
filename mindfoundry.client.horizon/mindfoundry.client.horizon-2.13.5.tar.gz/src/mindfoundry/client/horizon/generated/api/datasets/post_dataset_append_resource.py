from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.file_upload_form import FileUploadForm
from ...models.ingestion_process import IngestionProcess
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    id: int,
    multipart_data: FileUploadForm,
) -> Dict[str, Any]:
    url = "{}/datasets/{id}/append".format(client.base_url, id=id)

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


def _parse_response(*, response: httpx.Response) -> Optional[IngestionProcess]:
    if response.status_code == 200:
        response_200 = IngestionProcess.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[IngestionProcess]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    id: int,
    multipart_data: FileUploadForm,
) -> Response[IngestionProcess]:
    kwargs = _get_kwargs(
        client=client,
        id=id,
        multipart_data=multipart_data,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    id: int,
    multipart_data: FileUploadForm,
) -> Optional[IngestionProcess]:
    """Request body, upload options and return object are identical to the upload endpoint's.
    All of the following conditions must be met in order for the process to succeed:

    - The current user did not exhaust their data allowance;
    - The current user must be the same user that created the dataset in the first place
      (or a support user);
    - There are no running pipelines that use the given dataset `dataset_id`;
    - The upload process of `dataset_id` must be completed, i.e. there cannot be any
      non-completed ingestion process for that dataset;
    - New data must contain exactly the same columns of the same types w.r.t. existing
      data currently stored in the dataset;
    - ALL new data points must be at least as recent as the most recent row in the dataset;
    - If the dataset has unique indices, then new data must also have unique indices;
    - New data must have the same cadence as existing data;
    - The oldest data points in the new data must be exactly 0 or 1 cadence away from
      the most recent row in the dataset.

    If any one of the conditions above is not met, this method will fail with an error.
    The corresponding ingestion process will be still marked as completed, but its
    `last_update_error` field will report the same error. The dataset will still be accessible.
    """

    return sync_detailed(
        client=client,
        id=id,
        multipart_data=multipart_data,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    id: int,
    multipart_data: FileUploadForm,
) -> Response[IngestionProcess]:
    kwargs = _get_kwargs(
        client=client,
        id=id,
        multipart_data=multipart_data,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    id: int,
    multipart_data: FileUploadForm,
) -> Optional[IngestionProcess]:
    """Request body, upload options and return object are identical to the upload endpoint's.
    All of the following conditions must be met in order for the process to succeed:

    - The current user did not exhaust their data allowance;
    - The current user must be the same user that created the dataset in the first place
      (or a support user);
    - There are no running pipelines that use the given dataset `dataset_id`;
    - The upload process of `dataset_id` must be completed, i.e. there cannot be any
      non-completed ingestion process for that dataset;
    - New data must contain exactly the same columns of the same types w.r.t. existing
      data currently stored in the dataset;
    - ALL new data points must be at least as recent as the most recent row in the dataset;
    - If the dataset has unique indices, then new data must also have unique indices;
    - New data must have the same cadence as existing data;
    - The oldest data points in the new data must be exactly 0 or 1 cadence away from
      the most recent row in the dataset.

    If any one of the conditions above is not met, this method will fail with an error.
    The corresponding ingestion process will be still marked as completed, but its
    `last_update_error` field will report the same error. The dataset will still be accessible.
    """

    return (
        await asyncio_detailed(
            client=client,
            id=id,
            multipart_data=multipart_data,
        )
    ).parsed
