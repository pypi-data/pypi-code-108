import io
import time

import pandas as pd

from mindfoundry.client.horizon.generated import Client
from mindfoundry.client.horizon.generated.api.datasets import (
    delete_individual_dataset_resource,
    get_data_slice_resource,
    get_dataset_resource,
    get_individual_dataset_resource,
    post_dataset_append_resource,
    post_dataset_upload_resource,
)
from mindfoundry.client.horizon.generated.api.ingestion_processes import (
    get_individual_ingestion_process_resource,
)
from mindfoundry.client.horizon.generated.models import (
    AllDatasets,
    FileUploadForm,
    IndividualDataset,
    IngestionProcess,
    IngestionStatus,
)
from mindfoundry.client.horizon.generated.types import File

from .utils import (
    DEFAULT_UPLOAD_OPTIONS,
    assert_success,
    data_frame_to_buffer,
    return_value_or_raise_error,
)


class DatasetsClient:
    def __init__(self, client: Client):
        self._client = client

    def get_all(self) -> AllDatasets:
        datasets = get_dataset_resource.sync_detailed(client=self._client)
        return return_value_or_raise_error(datasets)

    def get(self, dataset_id: int) -> IndividualDataset:
        dataset = get_individual_dataset_resource.sync_detailed(
            client=self._client,
            id=dataset_id,
        )
        return return_value_or_raise_error(dataset)

    def delete(self, dataset_id: int) -> None:
        response = delete_individual_dataset_resource.sync_detailed(
            client=self._client,
            id=dataset_id,
        )
        assert_success(response)

    def get_data(self, dataset_id: int, start: int, stop: int) -> pd.DataFrame:
        all_data = get_data_slice_resource.sync_detailed(
            client=self._client,
            id=dataset_id,
            start=start,
            stop=stop,
        )
        file = return_value_or_raise_error(all_data)
        return pd.read_csv(file.payload, encoding="utf-8")

    def upload(self, df: pd.DataFrame, name: str) -> IndividualDataset:
        str_buffer = data_frame_to_buffer(df)
        ingestion_process = self._upload_csv(str_buffer, name)
        ingestion_process = self._wait_for_ingestion_process(ingestion_process.id)
        return self._resolve_ingestion_process(ingestion_process)

    def append(self, dataset_id: int, df: pd.DataFrame) -> IndividualDataset:
        str_buffer = data_frame_to_buffer(df)
        ingestion_process = self._append_csv(str_buffer, dataset_id)
        ingestion_process = self._wait_for_ingestion_process(ingestion_process.id)
        return self._resolve_ingestion_process(ingestion_process)

    def _append_csv(self, str_buffer: io.StringIO, dataset_id: int) -> IngestionProcess:
        ingestion_process = post_dataset_append_resource.sync_detailed(
            client=self._client,
            id=dataset_id,
            multipart_data=FileUploadForm(
                options=DEFAULT_UPLOAD_OPTIONS,
                file=File(
                    payload=str_buffer,
                    file_name=f"{dataset_id}.csv",
                    mime_type="text/csv",
                ),
            ),
        )
        return return_value_or_raise_error(ingestion_process)

    def _upload_csv(self, str_buffer: io.StringIO, name: str) -> IngestionProcess:
        ingestion_process = post_dataset_upload_resource.sync_detailed(
            client=self._client,
            multipart_data=FileUploadForm(
                options=DEFAULT_UPLOAD_OPTIONS,
                file=File(
                    payload=str_buffer,
                    file_name=name,
                    mime_type="text/csv",
                ),
            ),
        )
        return return_value_or_raise_error(ingestion_process)

    def _get_ingestion_process(self, ingestion_process_id: int) -> IngestionProcess:
        ingestion_process = get_individual_ingestion_process_resource.sync_detailed(
            client=self._client,
            id=ingestion_process_id,
        )
        return return_value_or_raise_error(ingestion_process)

    def _wait_for_ingestion_process(self, ingestion_process_id: int) -> IngestionProcess:
        ingestion_process = self._get_ingestion_process(ingestion_process_id)

        while ingestion_process.status not in (IngestionStatus.COMPLETED, IngestionStatus.ERROR):
            time.sleep(2)
            ingestion_process = self._get_ingestion_process(ingestion_process_id)

        return ingestion_process

    def _resolve_ingestion_process(self, ingestion_process: IngestionProcess) -> IndividualDataset:
        if ingestion_process.status == IngestionStatus.ERROR:
            raise RuntimeError(ingestion_process.error)

        if ingestion_process.last_update_error is not None:
            raise RuntimeError(ingestion_process.last_update_error)

        if ingestion_process.status == IngestionStatus.COMPLETED:
            assert isinstance(ingestion_process.dataset_id, int)
            return self.get(ingestion_process.dataset_id)

        raise RuntimeError(f"Invalid ingestion status reached: {ingestion_process.status}")
