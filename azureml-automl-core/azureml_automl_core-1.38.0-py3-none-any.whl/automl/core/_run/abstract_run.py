# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import Any, BinaryIO, Dict, List, Optional, TextIO, Union


class AbstractRun(ABC):
    """Abstract class exposing methods of azureml.core.Run used by AutoML."""

    @property
    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def status(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def add_properties(self, properties: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_properties(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def set_tags(self, tags: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_file_path(self, file_name: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_tags(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_metrics(self, name: Optional[str] = None, recursive: bool = False, run_type: Optional[Any] = None,
                    populate: bool = False) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_status(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def complete(self, _set_status: bool = True) -> None:
        raise NotImplementedError

    @abstractmethod
    def fail(self, error_details: Optional[Any] = None, error_code: Optional[Any] = None,
             _set_status: bool = True) -> None:
        raise NotImplementedError

    @abstractmethod
    def cancel(self) -> None:
        """Mark the run as canceled."""
        raise NotImplementedError

    @abstractmethod
    def flush(self):
        raise NotImplementedError

    @abstractmethod
    def log(self, name: str, value: Any, description: str = '') -> None:
        raise NotImplementedError

    @abstractmethod
    def log_accuracy_table(self, name: str, score: Any, description: str = '') -> None:
        raise NotImplementedError

    @abstractmethod
    def log_confusion_matrix(self, name: str, score: Any, description: str = '') -> None:
        raise NotImplementedError

    @abstractmethod
    def log_residuals(self, name: str, score: Any, description: str = '') -> None:
        raise NotImplementedError

    @abstractmethod
    def log_predictions(self, name: str, score: Any, description: str = '') -> None:
        raise NotImplementedError

    @abstractmethod
    def upload_file(self, name: str, path_or_stream: Union[str, TextIO, BinaryIO]) -> None:
        raise NotImplementedError

    @abstractmethod
    def upload_files(self, names: List[str],
                     path_or_streams: List[Union[str, TextIO, BinaryIO]],
                     return_artifacts: Optional[bool],
                     timeout_seconds: Optional[int]) -> None:
        raise NotImplementedError

    @abstractmethod
    def download_file(self, name: str, output_file_path: str, **kwargs: Any) -> None:
        raise NotImplementedError
