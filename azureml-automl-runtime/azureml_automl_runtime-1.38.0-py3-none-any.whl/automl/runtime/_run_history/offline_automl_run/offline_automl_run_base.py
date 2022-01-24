# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
from abc import ABC
from io import IOBase
from shutil import copyfile
from typing import Any, BinaryIO, Dict, List, Optional, TextIO, Union, cast

from azureml.automl.core._run import AbstractRun
from azureml.automl.core.shared import constants


class OfflineAutoMLRunBase(AbstractRun, ABC):
    """
    Base class for an offline, local AutoML run. This class exposes many of the same API hooks as an AzureML Run, but
    it supports these APIs using offline resources / without reliance on run history.
    This base class is used both by AutoML local and native client runs.
    """
    TAGS_FILE_NAME = "_tags.json"
    PROPERTIES_FILE_NAME = "_properties.json"
    METRICS_FILE_NAME = "_metrics.json"

    def __init__(self, run_id: str, run_folder: str) -> None:
        self._id = run_id
        if run_folder is None:
            raise ValueError('Must provide a valid run folder.')
        self.run_folder = os.path.abspath(run_folder)

    @property
    def id(self):
        return self._id

    @property
    def properties(self) -> Dict[str, Any]:
        return self.get_properties()

    @property
    def tags(self) -> Dict[str, Any]:
        return self.get_tags()

    def add_properties(self, properties: Dict[str, Any]) -> None:
        self._update_reserved_metadata_dict(OfflineAutoMLRunBase.PROPERTIES_FILE_NAME, properties)

    def get_properties(self) -> Dict[str, Any]:
        return self._read_reserved_metadata_dict(OfflineAutoMLRunBase.PROPERTIES_FILE_NAME)

    def set_tags(self, tags: Dict[str, Any]) -> None:
        self._update_reserved_metadata_dict(OfflineAutoMLRunBase.TAGS_FILE_NAME, tags)

    def get_file_path(self, file_name: str) -> str:
        return os.path.join(self.run_folder, file_name)

    def get_tags(self) -> Dict[str, Any]:
        return self._read_reserved_metadata_dict(OfflineAutoMLRunBase.TAGS_FILE_NAME)

    def get_metrics(self, name: Optional[str] = None, recursive: bool = False, run_type: Optional[Any] = None,
                    populate: bool = False) -> Dict[str, Any]:
        return self._read_reserved_metadata_dict(OfflineAutoMLRunBase.METRICS_FILE_NAME)

    def get_status(self) -> str:
        return self.get_tags().get('run_status', constants.Status.NotStarted)

    @property
    def status(self) -> str:
        return self.get_status()

    def start(self) -> None:
        pass

    def complete(self, _set_status: bool = True) -> None:
        tags = self.get_tags()
        tags['run_status'] = constants.Status.Completed
        self.set_tags(tags)

    def fail(self, error_details: Optional[Any] = None, error_code: Optional[Any] = None,
             _set_status: bool = True) -> None:
        tags = self.get_tags()
        tags['run_status'] = constants.Status.Terminated
        self.set_tags(tags)

    def cancel(self) -> None:
        tags = self.get_tags()
        tags['run_status'] = constants.Status.Terminated
        self.set_tags(tags)

    def flush(self) -> None:
        """For online runs, 'flush' sends all queued metrics requests to RH. For offline runs, there is no work to
        do here."""
        return

    def log(self, name: str, value: Any, description: str = '') -> None:
        # TODO: Verify that the other log methods work properly
        self._update_reserved_metadata_dict(OfflineAutoMLRunBase.METRICS_FILE_NAME, {name: value})

    def log_table(self, name: str, score: Any, description: str = '') -> None:
        """Passthrough log method to mimic RH's log_table functionality"""
        self.log(name, score, description)

    def log_accuracy_table(self, name: str, score: Any, description: str = '') -> None:
        """Passthrough to log method, because we shouldn't need to do anything special unlike SDK."""
        self.log(name, score, description)

    def log_horzion_table(self, name: str, score: Any, description: str = '') -> None:
        """Passthrough to log method, because we shouldn't need to do anything special unlike SDK."""
        self.log(name, score, description)

    def log_confusion_matrix(self, name: str, score: Any, description: str = '') -> None:
        """Passthrough to log method, because we shouldn't need to do anything special unlike SDK."""
        self.log(name, score, description)

    def log_residuals(self, name: str, score: Any, description: str = '') -> None:
        """Passthrough to log method, because we shouldn't need to do anything special unlike SDK."""
        self.log(name, score, description)

    def log_predictions(self, name: str, score: Any, description: str = '') -> None:
        """Passthrough to log method, because we shouldn't need to do anything special unlike SDK."""
        self.log(name, score, description)

    def upload_file(self, name: str, path_or_stream: Union[str, TextIO, BinaryIO]) -> None:
        # copy the file from local_path to the remote path within the run folder
        destination_file = os.path.join(self.run_folder, name)
        # in case the remote path contains some nested structure, we need to create those folders
        os.makedirs(os.path.dirname(destination_file), exist_ok=True)
        if isinstance(path_or_stream, str):
            copyfile(path_or_stream, destination_file)
        elif isinstance(path_or_stream, IOBase):
            raise ValueError("Not supported for now to upload a Stream.")

    def upload_files(self, names: List[str],
                     path_or_streams: List[Union[str, TextIO, BinaryIO]],
                     return_artifacts: Optional[bool],
                     timeout_seconds: Optional[int]) -> None:
        # copy a list of files from local_path to the remote path within the run folder
        for name, path_or_stream in zip(names, path_or_streams):
            self.upload_file(name, path_or_stream)

    def download_file(self, name: str, output_file_path: str, **kwargs: Any) -> None:
        source_file = os.path.join(self.run_folder, name)
        copyfile(source_file, output_file_path)

    def _update_reserved_metadata_dict(self, file_name: str, metadata_dict: Dict[str, Any]) -> None:
        existing_metadata_dict = self._read_reserved_metadata_dict(file_name)
        metadata_dict = {**existing_metadata_dict, **metadata_dict}
        self._store_reserved_metadata_obj_in_json(file_name, metadata_dict)

    def _read_reserved_metadata_dict(self, file_name: str) -> Dict[str, Any]:
        existing_dict = self._read_reserved_metadata_obj_from_json(file_name, {})
        return cast(Dict[str, Any], existing_dict)

    def _store_reserved_metadata_obj_in_json(self, file_name: str, obj: Any) -> None:
        file_path = os.path.join(self.run_folder, file_name)
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file_stream:
            file_stream.write(json.dumps(obj))

    def _read_reserved_metadata_obj_from_json(self, file_name: str, default: Any) -> Optional[Any]:
        file_path = os.path.join(self.run_folder, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r") as file_stream:
                content = file_stream.read()
                return json.loads(content)
        else:
            return default
