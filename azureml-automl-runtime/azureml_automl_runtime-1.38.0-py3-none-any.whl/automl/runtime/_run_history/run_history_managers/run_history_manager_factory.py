# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os

from azureml.automl.core.constants import RunHistoryEnvironmentVariableNames
from azureml.automl.runtime._run_history.run_history_managers.offline_run_history_manager import \
    OfflineRunHistoryManager
from azureml.automl.runtime._run_history.run_history_managers.run_history_manager import \
    RunHistoryManager
from azureml.automl.runtime._run_history.run_history_managers.run_history_manager_base import \
    RunHistoryManagerBase


class RunHistoryManagerFactory:
    """Factory for producing an AutoML Run History manager."""

    @staticmethod
    def get_run_history_manager() -> RunHistoryManagerBase:
        """Get a Run History manager."""
        # If there is run history data on local disk, return a run history manager leveraging this data
        run_history_data_path = os.environ.get(RunHistoryEnvironmentVariableNames.AZUREML_AUTOML_RUN_HISTORY_DATA_PATH)
        if run_history_data_path:
            return OfflineRunHistoryManager(run_history_data_path)

        return RunHistoryManager()
