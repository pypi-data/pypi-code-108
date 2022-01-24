# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Context manager that wraps an AutoML run context."""
from typing import Any, Optional
import time

from azureml.automl.runtime.automl_run_context import AutoMLAbstractRunContext
from azureml.core import Run


class AzureAutoMLRunContext(AutoMLAbstractRunContext):

    def __init__(self, run: Optional[Run], is_adb_run: bool = False) -> None:
        """
        Create an AzureAutoMLRunContext object that wraps a run context.

        :param run: the run context to use
        :param is_adb_run: whether we are running in Azure DataBricks or not
        """
        super().__init__()
        self._run = run
        self._is_adb_run = is_adb_run

        # Refresh the run context after 15 minutes if running under adb
        self._timeout_interval = 900.0
        self._last_refresh = 0.0

    def _get_run_internal(self) -> Run:
        """Retrieve a run context if needed and return it."""
        # In case we use get_run in nested with statements, only get the run context once

        if self._refresh_needed():
            self._last_refresh = time.time()
            self._run = Run.get_context()
        return self._run

    def _refresh_needed(self) -> bool:
        if self._run is None:
            return True

        if self._is_adb_run:
            return (time.time() - self._last_refresh) > self._timeout_interval

        return False

    def save_model_output(self, fitted_pipeline: Any, remote_path: str, working_dir: str) -> None:
        """
        Save model output to provided path.

        :param fitted_pipeline:
        :param remote_path:
        :param working_dir:
        :return:
        :raises azureml.exceptions.ServiceException
        """
        super().save_model_output(fitted_pipeline, remote_path, working_dir)
