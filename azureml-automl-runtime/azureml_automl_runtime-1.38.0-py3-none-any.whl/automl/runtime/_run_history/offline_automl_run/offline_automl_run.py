# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from datetime import datetime, timezone
from typing import Any, BinaryIO, List, Optional, TextIO, Union, cast

from azureml.automl.runtime._run_history.offline_automl_run.offline_automl_run_base import OfflineAutoMLRunBase


class OfflineAutoMLRun(OfflineAutoMLRunBase):
    """
    Class for an offline, local AutoML run. This class exposes many of the same API hooks as an AzureML Run, but
    it supports these APIs using offline resources / without reliance on run history.
    """

    UPLOADS_FILE_NAME = '_uploaded_files.json'

    def __init__(self, run_id: str, run_folder: str) -> None:
        super().__init__(run_id, run_folder)

        self.created_time = datetime.now().replace(tzinfo=timezone.utc)
        self.start_time = None  # type: Optional[datetime]
        self.end_time = None  # type: Optional[datetime]
        self.error_code = None
        self.error_details = None

    def start(self) -> None:
        """Start the run."""
        self.start_time = datetime.now().replace(tzinfo=timezone.utc)

    def complete(self, _set_status: bool = True) -> None:
        """Complete the run."""
        self.end_time = datetime.now().replace(tzinfo=timezone.utc)
        super().complete(_set_status)

    def fail(self, error_details: Optional[Any] = None, error_code: Optional[Any] = None,
             _set_status: bool = True) -> None:
        """Fail the run."""
        self.end_time = datetime.now().replace(tzinfo=timezone.utc)
        self.error_details = error_details
        self.error_code = error_code
        super().fail(error_details, error_code, _set_status)

    def upload_file(self, name: str, path_or_stream: Union[str, TextIO, BinaryIO]) -> None:
        """Simulate an AzureML run file upload. File will be stored on disk and associated with this run."""
        super().upload_file(name, path_or_stream)
        self._store_uploaded_file_name(name)

    def get_uploaded_file_names(self) -> List[Any]:
        """Get the list of uploaded file names."""
        return self._read_reserved_metadata_list(OfflineAutoMLRun.UPLOADS_FILE_NAME)

    def _append_reserved_metadata_list(self, file_name: str, item: str) -> None:
        metadata_list = self._read_reserved_metadata_list(file_name)
        metadata_list.append(item)
        self._store_reserved_metadata_obj_in_json(file_name, metadata_list)

    def _read_reserved_metadata_list(self, file_name: str) -> List[Any]:
        existing_list = self._read_reserved_metadata_obj_from_json(file_name, [])
        return cast(List[Any], existing_list)

    def _store_uploaded_file_name(self, file_name: str) -> None:
        self._append_reserved_metadata_list(OfflineAutoMLRun.UPLOADS_FILE_NAME, file_name)
