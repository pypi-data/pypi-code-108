from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.file_upload_form import FileUploadForm
from ...models.ingestion_process import IngestionProcess
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    multipart_data: FileUploadForm,
) -> Dict[str, Any]:
    url = "{}/datasets/upload".format(client.base_url)

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
    multipart_data: FileUploadForm,
) -> Response[IngestionProcess]:
    kwargs = _get_kwargs(
        client=client,
        multipart_data=multipart_data,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    multipart_data: FileUploadForm,
) -> Optional[IngestionProcess]:
    """An IngestionProcess will be returned, which you can query via the `/ingestionProcess/{id}`
    endpoint until its `status` value is \"completed\". Then take the `datasetId` value and use
    it with the `/datasets/{id}` endpoint to get information on the dataset.

    For example, in python:

        import pandas as pd
        import io
        import json
        import requests
        from time import sleep

        df = pd.DataFrame({\"time\": [\"1/1/1\", \"2/1/1\"], \"x\": [1, 2]})
        str_buffer = io.StringIO(df.to_csv(encoding=\"utf-8\", index=False))
        str_buffer.seek(0)
        str_buffer.name = \"Your Data Set Name\"

        upload_options = {
            \"missingDataStrategy\": {
                \"ffill\": {\"enabled\": True},
                \"replaceMissing\": {\"enabled\": True, \"replaceWith\": 42},
            },
        }

        headers = {\"x-apikey\": \"Paste your API Key here\"}

        base_url = \"https://horizon.mindfoundry.ai\"  # Amend if necessary
        rv = requests.post(
            url=f\"{base_url}/api/datasets/upload\",
            files={\"file\": str_buffer},
            data={\"options\": json.dumps(upload_options)},
            headers=headers,
        )
        ingestion_process = rv.json()
        ingestion_id = ingestion_process[\"id\"]

        while ingestion_process[\"status\"] not in [\"completed\", \"error\"]:
            sleep(0.5)
            rv = requests.get(
                url=f\"{base_url}/api/ingestionProcesses/{ingestion_id}\",
                headers=headers,
            )
            ingestion_process = rv.json()

        if ingestion_process[\"status\"] == \"completed\":
            dataset_id = ingestion_process[\"datasetId\"]
            rv = requests.get(url=f\"{base_url}/api/datasets/{dataset_id}\", headers=headers)
            dataset = rv.json()
        else:
            raise Exception(ingestion_process[\"error\"])
    """

    return sync_detailed(
        client=client,
        multipart_data=multipart_data,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    multipart_data: FileUploadForm,
) -> Response[IngestionProcess]:
    kwargs = _get_kwargs(
        client=client,
        multipart_data=multipart_data,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    multipart_data: FileUploadForm,
) -> Optional[IngestionProcess]:
    """An IngestionProcess will be returned, which you can query via the `/ingestionProcess/{id}`
    endpoint until its `status` value is \"completed\". Then take the `datasetId` value and use
    it with the `/datasets/{id}` endpoint to get information on the dataset.

    For example, in python:

        import pandas as pd
        import io
        import json
        import requests
        from time import sleep

        df = pd.DataFrame({\"time\": [\"1/1/1\", \"2/1/1\"], \"x\": [1, 2]})
        str_buffer = io.StringIO(df.to_csv(encoding=\"utf-8\", index=False))
        str_buffer.seek(0)
        str_buffer.name = \"Your Data Set Name\"

        upload_options = {
            \"missingDataStrategy\": {
                \"ffill\": {\"enabled\": True},
                \"replaceMissing\": {\"enabled\": True, \"replaceWith\": 42},
            },
        }

        headers = {\"x-apikey\": \"Paste your API Key here\"}

        base_url = \"https://horizon.mindfoundry.ai\"  # Amend if necessary
        rv = requests.post(
            url=f\"{base_url}/api/datasets/upload\",
            files={\"file\": str_buffer},
            data={\"options\": json.dumps(upload_options)},
            headers=headers,
        )
        ingestion_process = rv.json()
        ingestion_id = ingestion_process[\"id\"]

        while ingestion_process[\"status\"] not in [\"completed\", \"error\"]:
            sleep(0.5)
            rv = requests.get(
                url=f\"{base_url}/api/ingestionProcesses/{ingestion_id}\",
                headers=headers,
            )
            ingestion_process = rv.json()

        if ingestion_process[\"status\"] == \"completed\":
            dataset_id = ingestion_process[\"datasetId\"]
            rv = requests.get(url=f\"{base_url}/api/datasets/{dataset_id}\", headers=headers)
            dataset = rv.json()
        else:
            raise Exception(ingestion_process[\"error\"])
    """

    return (
        await asyncio_detailed(
            client=client,
            multipart_data=multipart_data,
        )
    ).parsed
