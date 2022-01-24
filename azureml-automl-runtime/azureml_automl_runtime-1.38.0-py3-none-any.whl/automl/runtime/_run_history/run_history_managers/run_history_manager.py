# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.automl.runtime._run_history.run_history_managers.run_history_manager_base import RunHistoryManagerBase
from azureml.core import Run


class RunHistoryManager(RunHistoryManagerBase):
    """Default Run History manager that pulls from Run History service."""

    def get_context(self) -> Run:
        """Get the current run."""
        return Run.get_context()
