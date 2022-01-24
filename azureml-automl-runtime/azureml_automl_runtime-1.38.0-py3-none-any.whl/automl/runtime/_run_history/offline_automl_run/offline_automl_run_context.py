# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.automl.runtime._run_history.offline_automl_run.offline_automl_run import OfflineAutoMLRunBase
from azureml.automl.runtime.automl_run_context import AutoMLAbstractRunContext


class OfflineAutoMLRunContext(AutoMLAbstractRunContext):
    """Run context for an offline AutoML run."""

    def __init__(self, run: OfflineAutoMLRunBase) -> None:
        super().__init__()
        self._run = run

    def _get_run_internal(self) -> OfflineAutoMLRunBase:
        return self._run
