# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os

from azureml.automl.core.constants import RunHistoryEnvironmentVariableNames
from azureml.automl.runtime._run_history.offline_automl_run import OfflineAutoMLRun, OfflineAutoMLRunUtil
from azureml.automl.runtime._run_history.run_history_managers.run_history_manager_base import RunHistoryManagerBase


class OfflineRunHistoryManager(RunHistoryManagerBase):
    """Offline Run History manager that pulls from a run history data folder on local disk."""

    def __init__(self, run_history_data_path: str) -> None:
        self._run_history_data_path = run_history_data_path

    def get_context(self) -> OfflineAutoMLRun:
        """Get the current run."""
        run_id = os.environ[RunHistoryEnvironmentVariableNames.AZUREML_RUN_ID]
        return OfflineAutoMLRunUtil.get_run(self._run_history_data_path, run_id)
