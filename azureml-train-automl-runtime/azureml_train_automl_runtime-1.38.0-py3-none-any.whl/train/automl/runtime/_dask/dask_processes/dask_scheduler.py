# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.train.automl.runtime._dask.constants import Constants
from azureml.train.automl.runtime._dask.dask_processes.dask_process_controller import DaskProcessController


class DaskScheduler:
    """Handles Dask scheduler operations."""

    def __init__(self):
        self._scheduler_process = DaskProcessController()

    def start(self) -> None:
        """Start the scheduler."""
        self._scheduler_process.start_process('dask-scheduler', [], {'port': str(Constants.SCHEDULER_PORT)})

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        self._scheduler_process.kill()
