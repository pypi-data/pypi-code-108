# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.core import Run
from azureml.train.automl.run import AutoMLRun
from azureml.train.automl.runtime._synchronizable_runs.synchronizable_run import SynchronizableRun


class SynchronizableAutoMLRun(SynchronizableRun, AutoMLRun):
    """
    This is a synchronizable, AutoML run. Please see both SynchronizableRun and AutoMLRun for more information
    on both of these classes.
    """

    def __init__(self, experiment, run_id, **kwargs):
        # Initialize a Run object. This makes a call to RH to fetch the run
        run = Run(experiment, run_id)

        # Initialize subclasses. These initializations use run_dto, so they won't trigger calls to RH
        SynchronizableRun.__init__(self, experiment, run_id, _run_dto=run._client.run_dto, **kwargs)
        AutoMLRun.__init__(self, experiment, run_id, _run_dto=run._client.run_dto, **kwargs)
        self._kwargs = kwargs

    def to_automl_run(self) -> AutoMLRun:
        """Return an AutoML Run (that is not synchronizable)."""
        automl_run = AutoMLRun(
            self.experiment,
            self.id,
            _run_dto=self._client.run_dto,
            **self._kwargs)
        automl_run._cached_best_model = self._cached_best_model
        automl_run._cached_best_run = self._cached_best_run
        return automl_run
