# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Distributed setup run."""
import json
import logging
import os
from typing import Any, Callable, Optional

from azureml._tracing import get_tracer
from azureml.automl.core._logging import log_server
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.telemetry_activity_logger import TelemetryActivityLogger
from azureml.core import Run, Dataset
from azureml.data import TabularDataset
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.runtime._automl_job_phases import DistributedFeaturizationPhase, DistributedPreparationPhase
from azureml.train.automl.runtime._worker_initiator import EXPERIMENT_STATE_PLUGIN
from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext
from azureml.train.automl.runtime._entrypoints import entrypoint_util
from dask.distributed import WorkerPlugin
from dask.distributed import get_client

from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.faults_verifier import VerifierManager
from azureml.automl.runtime.shared.lazy_azure_blob_cache_store import LazyAzureBlobCacheStore

logger = logging.getLogger(__name__)
activity_logger = TelemetryActivityLogger()
tracer = get_tracer(__name__)


class _LogInitializerWorkerPlugin(WorkerPlugin):
    """A worker plugin to initalize logging on dask workers for remote runs."""
    def __init__(self, run_id, automl_settings_str):
        self._run_id = run_id
        self._automl_settings_str = automl_settings_str

    def setup(self, worker):
        entrypoint_util.initialize_log_server(self._run_id, self._automl_settings_str)
        log_server.update_custom_dimension(pid=os.getpid())


class ExperimentStatePlugin(WorkerPlugin):
    def __init__(self, workspace_getter: Callable[..., Any],
                 parent_run_id: str,
                 training_dataset : TabularDataset,
                 validation_dataset : TabularDataset,
                 automl_settings : AzureAutoMLSettings):
        self.workspace_getter = workspace_getter
        self.parent_run_id = parent_run_id
        self.training_dataset = TabularDataset._create(training_dataset._dataflow,
                                                       training_dataset._properties,
                                                       telemetry_info=training_dataset._telemetry_info)
        self.validation_dataset = TabularDataset._create(validation_dataset._dataflow,
                                                         validation_dataset._properties,
                                                         telemetry_info=validation_dataset._telemetry_info)\
            if validation_dataset is not None else None
        self.automl_settings = automl_settings


def execute(
        script_directory: Optional[str],
        dataprep_json: str,
        automl_settings: str,
) -> None:
    setup_run = Run.get_context()
    workspace = setup_run.experiment.workspace
    try:
        verifier = VerifierManager()
        parent_run, automl_settings_obj, cache_store = entrypoint_util.init_wrapper(
            setup_run,
            automl_settings,
            script_directory
        )

        # this is a dirty work around. See 1484325
        automl_settings_obj.n_cross_validations = None

        if not isinstance(cache_store, LazyAzureBlobCacheStore):
            data_store = entrypoint_util._get_cache_data_store(setup_run.experiment)
            cache_store = LazyAzureBlobCacheStore(data_store, parent_run.id)

        Contract.assert_type(value=cache_store, name='cache_store',
                             expected_types=LazyAzureBlobCacheStore)

        expr_store = ExperimentStore(cache_store, read_only=False)
        dataprep_json_obj = json.loads(dataprep_json)
        training_data_obj = dataprep_json_obj.get('training_data', {})
        training_dataset_id = training_data_obj.get('datasetId', None)
        validation_dataset_obj = dataprep_json_obj.get('validation_data', {})
        validation_dataset_id = validation_dataset_obj.get('datasetId', None)

        Contract.assert_non_empty(value=training_dataset_id, name="training_dataset_id")
        training_dataset = Dataset.get_by_id(workspace, training_dataset_id)

        if validation_dataset_id:
            validation_dataset = Dataset.get_by_id(workspace, validation_dataset_id)
        else:
            validation_dataset = None

        logger.info("Fetching grain keys and values")
        all_grain_key_values = training_dataset.get_partition_key_values()
        logger.info("total grains for the current experiment = {}".format(len(all_grain_key_values)))

        # register plug-ins required for dask
        client = get_client()
        logInitializerPlugin = _LogInitializerWorkerPlugin(setup_run.id,
                                                           automl_settings)
        client.register_worker_plugin(logInitializerPlugin)

        experiment_state_plugin = ExperimentStatePlugin(lambda: Run.get_context().experiment.workspace,
                                                        parent_run.id,
                                                        training_dataset,
                                                        validation_dataset,
                                                        automl_settings_obj)
        client.register_worker_plugin(experiment_state_plugin, EXPERIMENT_STATE_PLUGIN)

        DistributedPreparationPhase.run(lambda: Run.get_context().experiment.workspace,
                                        Run.get_context().experiment.name,
                                        parent_run.id,
                                        automl_settings_obj,
                                        training_dataset,
                                        validation_dataset,
                                        all_grain_key_values,
                                        verifier)

        # We need to unload the experiment store to ensure it is
        # available in worker processes during the featurization phase.
        expr_store.unload()
        expr_store.load()

        # if data was prepared, use it, otherwise use training data.
        if expr_store.data.partitioned._prepared_train_dataset_id:
            prepared_train_data = expr_store.data.partitioned.get_prepared_train_dataset(workspace)
            prepared_valid_data = expr_store.data.partitioned.get_prepared_valid_dataset(workspace)
        else:
            prepared_train_data = training_dataset
            prepared_valid_data = validation_dataset

        DistributedFeaturizationPhase.run(lambda: Run.get_context().experiment.workspace,
                                          setup_run,
                                          parent_run.id,
                                          automl_settings_obj,
                                          prepared_train_data,
                                          prepared_valid_data,
                                          all_grain_key_values)

        parent_run_context = AzureAutoMLRunContext(parent_run)
        verifier.write_result_file(parent_run_context)
        expr_store.unload()
    except Exception as e:
        logger.error("AutoML distributed setup script terminated with an exception of type: {}".format(type(e)))
        run_lifecycle_utilities.fail_run(setup_run, e, update_run_properties=True)
        raise
    finally:
        # Reset the singleton for subsequent usage.
        ExperimentStore.reset()
