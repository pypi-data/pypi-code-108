from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.classification_prediction_form import ClassificationPredictionForm
from ...models.classification_prediction_result import ClassificationPredictionResult
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    id: int,
    multipart_data: ClassificationPredictionForm,
) -> Dict[str, Any]:
    url = "{}/pipelines/{id}/expert/classification/predict".format(client.base_url, id=id)

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


def _parse_response(*, response: httpx.Response) -> Optional[ClassificationPredictionResult]:
    if response.status_code == 200:
        response_200 = ClassificationPredictionResult.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[ClassificationPredictionResult]:
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
    multipart_data: ClassificationPredictionForm,
) -> Response[ClassificationPredictionResult]:
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
    multipart_data: ClassificationPredictionForm,
) -> Optional[ClassificationPredictionResult]:
    """It uses features inferred from on the original pipeline dataset, but a new
    model is trained on the whole pipeline dataset and tested on the uploaded dataset.

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
    multipart_data: ClassificationPredictionForm,
) -> Response[ClassificationPredictionResult]:
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
    multipart_data: ClassificationPredictionForm,
) -> Optional[ClassificationPredictionResult]:
    """It uses features inferred from on the original pipeline dataset, but a new
    model is trained on the whole pipeline dataset and tested on the uploaded dataset.

    """

    return (
        await asyncio_detailed(
            client=client,
            id=id,
            multipart_data=multipart_data,
        )
    ).parsed
