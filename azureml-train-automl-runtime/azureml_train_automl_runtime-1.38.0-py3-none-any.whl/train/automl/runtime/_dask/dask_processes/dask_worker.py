# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from azureml.train.automl.runtime._dask.constants import Constants
from azureml.train.automl.runtime._dask.dask_processes.dask_process_controller import DaskProcessController


class DaskWorker:
    """Handles Dask worker  operations."""

    def __init__(self):
        self._worker_process = DaskProcessController()

    def start(self, scheduler_ip: str) -> None:
        """Start the worker."""
        self._worker_process.start_process(
            'dask-worker',
            ['tcp://{}:{}'.format(scheduler_ip, Constants.SCHEDULER_PORT)],
            {
                'nprocs': str(os.cpu_count()),
                'death-timeout': '30'
            }
        )

    def wait(self) -> None:
        """Wait for the worker to termminate."""
        self._worker_process.wait()
