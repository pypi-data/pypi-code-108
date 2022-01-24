# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod

from azureml.automl.core._run import RunType


class RunHistoryManagerBase(ABC):
    """Base class for managing AutoML interactions with Run History."""

    @abstractmethod
    def get_context(self) -> RunType:
        """Get the current run."""
        raise NotImplementedError
