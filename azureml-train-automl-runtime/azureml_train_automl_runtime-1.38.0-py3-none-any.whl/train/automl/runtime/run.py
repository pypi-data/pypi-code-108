# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains functionality for managing automated ML runs in Azure Machine Learning.

This module allows you to start or stop automated ML runs, monitor run status, and retrieve model output.
"""
import json
import tempfile
from azureml.automl.runtime.data_context import TransformedDataContext
from azureml._restclient.constants import RunStatus
from azureml.train.automl.run import AutoMLRun as _AutoMLRun
from azureml.train.automl import _constants_azureml, _logging, constants  # type: ignore
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings

# Task: 287629 Remove when Mix-in available
STATUS = 'status'

RUNNING_STATES = [RunStatus.STARTING, RunStatus.PREPARING, RunStatus.RUNNING,
                  RunStatus.PROVISIONING, RunStatus.QUEUED]
POST_PROCESSING_STATES = [RunStatus.FINALIZING, RunStatus.CANCEL_REQUESTED]

CONTINUE_EXPERIMENT_KEY = 'continue'
CONTINUE_EXPERIMENT_SET = 'Set'
CONTINUE_EXPERIMENT_STATUS_KEY = '_aml_system_automl_status'


class AutoMLRun(_AutoMLRun):
    """
    Represents an automated ML experiment run in Azure Machine Learning.

    The AutoMLRun class can be used to manage a run, check run status, and retrieve run
    details once an automated ML run is submitted. For more information on working with experiment runs,
    see the :class:`azureml.core.run.Run` class.

    :param experiment: The experiment associated with the run.
    :type experiment: azureml.core.Experiment
    :param run_id: The ID of the run.
    :type run_id: str
    """

    def clean_preprocessor_cache(self):
        """Clean the transformed, preprocessed data cache."""
        try:
            from azureml.train.automl.runtime._cachestorefactory import CacheStoreFactory
            properties = self.get_properties()

            if 'AMLSettingsJsonString' not in properties:
                compute_target = constants.ComputeTargets.LOCAL
            else:
                automl_settings = AzureAutoMLSettings(
                    experiment=self.experiment,
                    **json.loads(properties['AMLSettingsJsonString']))
                compute_target = automl_settings.compute_target

            # TODO: Can we have a cleaner way of doing this?
            with tempfile.TemporaryDirectory() as tempdir:
                cache_store = CacheStoreFactory.get_cache_store(
                    temp_location=str(tempdir),
                    run_target=compute_target,
                    run_id=self.run_id,
                    data_store=self.experiment.workspace.get_default_datastore())
                transformed_data_context = TransformedDataContext(
                    X={},
                    cache_store=cache_store)
                transformed_data_context.cleanup()
        except Exception:
            pass
