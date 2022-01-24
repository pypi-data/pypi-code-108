# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Any, Callable, Tuple

from azureml.core import Workspace
from azureml._restclient.models import DataStore

from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.shared.lazy_azure_blob_cache_store import LazyAzureBlobCacheStore

logger = logging.getLogger(__name__)

# these are worker process global variables that are supposed to be initialized/set only once per worker process
default_datastore_for_worker = None
workspace_for_worker = None
expr_store_for_worker = None

EXPERIMENT_STATE_PLUGIN = "experiment_state_plugin"
STAT_CALCULATOR_PLUGIN = 'stat_calculator_plugin'


def get_worker_variables(workspace_getter: Callable[..., Any],
                         parent_run_id: str) -> Tuple[DataStore, Workspace, ExperimentStore]:
    global default_datastore_for_worker
    global workspace_for_worker
    global expr_store_for_worker

    if default_datastore_for_worker is None:
        # Use one for lifetime of worker process instead of one per grain
        logger.info("creating workspace for the worker process")
        workspace_for_worker = workspace_getter()
        default_datastore_for_worker = workspace_for_worker.get_default_datastore()
        cache_store = LazyAzureBlobCacheStore(default_datastore_for_worker, parent_run_id)
        expr_store_for_worker = ExperimentStore(cache_store, read_only=False)

    return default_datastore_for_worker, workspace_for_worker, expr_store_for_worker
