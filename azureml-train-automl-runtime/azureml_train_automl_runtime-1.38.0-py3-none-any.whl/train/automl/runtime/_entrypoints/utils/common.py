# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods for AutoML remote runs."""
import json
import logging
import os
import re
import sys
import tempfile
import time
from typing import Any, Optional, Tuple

from azureml._history.utils.constants import LOGS_AZUREML_DIR
from azureml._tracing import get_tracer
from azureml.automl.core._logging import log_server
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.constants import TelemetryConstants
from azureml.automl.core.shared.exceptions import AutoMLException, CacheException, UserException
from azureml.automl.core.shared.telemetry_activity_logger import TelemetryActivityLogger
from azureml.automl.runtime import training_utilities
from azureml.automl.runtime._data_definition import RawExperimentData
from azureml.automl.runtime.faults_verifier import VerifierManager
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.core import Datastore, Experiment, Run
from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore
from azureml.data.constants import WORKSPACE_BLOB_DATASTORE
from azureml.train.automl import _logging  # type: ignore
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl._constants_azureml import CodePaths
from azureml.train.automl.constants import ComputeTargets
from azureml.train.automl.exceptions import ClientException
from azureml.train.automl.runtime._cachestorefactory import CacheStoreFactory
from azureml.train.automl.runtime._data_preparer import DataPreparer
from azureml.train.automl.runtime.utilities import _load_user_script
from azureml.train.automl.utilities import _get_package_version
from msrest.exceptions import HttpOperationError

CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA = '_CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA_'

# The base dataset object can be cached in the setup iteration (to be later re-used during model training),
# with the following key
DATASET_BASE_CACHE_KEY = 'dataset_cached_object'

logger = logging.getLogger(__name__)
activity_logger = TelemetryActivityLogger()
tracer = get_tracer(__name__)


def init_wrapper(
        current_run: Run,
        automl_settings_str: str,
        script_directory: Optional[str],
        code_path: Optional[str] = None,
        load_cache: bool = True,
        **kwargs: Any
) -> Tuple[Run, AzureAutoMLSettings, CacheStore]:
    """Initialize common variables across remote wrappers."""
    with tracer.start_as_current_span(
            TelemetryConstants.SPAN_FORMATTING.format(
                TelemetryConstants.COMPONENT_NAME, TelemetryConstants.RUN_INITIALIZATION
            ),
            user_facing_name=TelemetryConstants.RUN_INITIALIZATION_USER_FACING
    ):
        pkg_ver = _get_package_version()
        logger.info('Using SDK version {}'.format(pkg_ver))

        _init_directory(directory=script_directory)

        parent_run_id = get_parent_run_id(current_run.id)
        parent_run = Run(current_run.experiment, parent_run_id)

        automl_settings_obj = initialize_log_server(current_run.id, automl_settings_str, code_path=code_path)

        # cache_store_parent_run_id kwarg is only expected to be used in backwards compatibility e2e tests,
        # it is not expected to be used in production scenarios.
        cache_store_parent_run_id = kwargs.pop('cache_store_parent_run_id', parent_run_id)
        use_fd_cache = False
        # This attribute is dynamically added for flighting purposes from JOS
        # and/or as input from AutoMLSettings. Once we are confident in implementation
        # it will no longer need to be checked.
        if hasattr(automl_settings_obj, "use_fd_cache"):
            use_fd_cache = True
        cache_store = init_cache_store(
            parent_run.experiment,
            parent_run_id=cache_store_parent_run_id,
            use_fd_cache=use_fd_cache
        )
        if load_cache:
            cache_store.load()

    return parent_run, automl_settings_obj, cache_store


def get_raw_experiment_data(data_preparer: Optional[DataPreparer],
                            automl_settings_obj: AzureAutoMLSettings,
                            script_directory: Optional[str],
                            entry_point: Optional[str]) -> RawExperimentData:
    if data_preparer:
        raw_experiment_data = data_preparer.prepare_raw_experiment_data(automl_settings_obj)
    else:
        if script_directory is None:
            script_directory = ""
        if entry_point is None:
            entry_point = ""
        script_path = os.path.join(script_directory, entry_point)
        if script_path is None:
            script_path = '.'
        user_module = _load_user_script(script_path, False)
        data_dict = training_utilities._extract_user_data(user_module)
        raw_experiment_data = RawExperimentData.create(
            data_dict,
            automl_settings_obj.label_column_name,
            automl_settings_obj.weight_column_name,
            automl_settings_obj.validation_size,
            automl_settings_obj.n_cross_validations)

    return raw_experiment_data


def init_cache_store(experiment: Experiment, parent_run_id: str, use_fd_cache: bool = False) -> CacheStore:
    cache_data_store = _get_cache_data_store(experiment)
    return _get_cache_store(data_store=cache_data_store, run_id=parent_run_id, use_fd_cache=use_fd_cache)


def _get_cache_store(
    data_store: Optional[AbstractAzureStorageDatastore],
    run_id: str,
    use_fd_cache: bool = False
) -> CacheStore:
    cache_location = str(tempfile.mkdtemp())
    return CacheStoreFactory.get_cache_store(
        temp_location=cache_location,
        run_target=ComputeTargets.AMLCOMPUTE,
        run_id=run_id,
        data_store=data_store,
        use_fd_cache=use_fd_cache
    )


def _get_cache_data_store(experiment: Experiment) -> Optional[AbstractAzureStorageDatastore]:
    data_store = None  # type: Optional[AbstractAzureStorageDatastore]
    start = time.time()
    try:
        data_store = Datastore.get(experiment.workspace, WORKSPACE_BLOB_DATASTORE)
        logger.info('Successfully got the cache data store, caching enabled.')
    except HttpOperationError as response_exception:
        logging_utilities.log_traceback(response_exception, logger)
        if response_exception.response.status_code >= 500:
            raise
        else:
            raise UserException.from_exception(response_exception).with_generic_msg(
                'Failed to get default datastore from Datastore Service. HTTP Status code: {}'.format(
                    response_exception.response.status_code)
            )
    end = time.time()
    logger.info('Took {} seconds to retrieve cache data store'.format(end - start))
    return data_store


def _init_logger() -> None:
    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter(fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
                                  datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    log_server.add_handler('stdout', handler)


def initialize_log_server(
        current_run_id: str,
        automl_settings: str,
        parent_run_id: Optional[str] = None,
        code_path: Optional[str] = CodePaths.REMOTE
) -> AzureAutoMLSettings:
    """
    Use automl_settings (as string) to initialize log_server.
    Side effects to modify a few automlsettings, create a folder, and update custom dimensions

    :param current_run_id: The run id of the run in context.
    :param automl_settings: The string of settings as prepared by JOS to be used to initialize
        custom dimensions, determine logging file names, and enable/disable telemetry.
    :param parent_run_id: The parentr un id of the current run in context.
    :param code_path: The code path of the run in context.
    :returns: The modified automl_settings as an AzureAutoMLSettings object.
    """
    if not os.path.exists(LOGS_AZUREML_DIR):
        os.makedirs(LOGS_AZUREML_DIR, exist_ok=True)
    _init_logger()

    # Don't reuse path from user's local machine for remote runs
    automl_settings_obj = AzureAutoMLSettings.from_string_or_dict(automl_settings, overrides={
        'debug_log': os.path.join(LOGS_AZUREML_DIR, "azureml_automl.log"),
        'path': tempfile.mkdtemp()
    })

    # enable traceback logging for remote runs
    os.environ['AUTOML_MANAGED_ENVIRONMENT'] = '1'

    if parent_run_id is None:
        parent_run_id = get_parent_run_id(current_run_id)

    _logging.set_run_custom_dimensions(
        automl_settings=automl_settings_obj,
        parent_run_id=parent_run_id,
        child_run_id=current_run_id,
        code_path=code_path)

    return automl_settings_obj


def _init_directory(directory: Optional[str]) -> str:
    if directory is None:
        directory = os.getcwd()
        logger.info('Directory was None, using current working directory.')

    sys.path.append(directory)
    # create the outputs folder
    logger.info('Creating output folder.')
    os.makedirs('./outputs', exist_ok=True)
    return directory


def get_parent_run_id(run_id: str) -> str:
    """
    Code for getting the AutoML parent run-id from the child run-id.
    :param run_id: This is in format AutoML_<GUID>_*
    :type run_id: str
    :return: str
    """
    try:
        return re.match("((?:AutoML_)?[a-zA-Z0-9-]+)_.+", run_id).group(1)  # type: ignore
    except (IndexError, AttributeError) as e:
        raise ClientException.from_exception(e, "Malformed AutoML child run-id passed", has_pii=False)


def modify_settings_for_streaming(
        automl_settings_obj: AzureAutoMLSettings,
        dataprep_json: str
) -> None:
    """called only from training runs"""
    automl_settings_obj.enable_streaming = True
    # check if UX and update the settings appropriately
    dataprep_json_obj = json.loads(dataprep_json)
    if 'activities' not in dataprep_json_obj:
        # for UI we need to set the label_column_name
        if automl_settings_obj.label_column_name is None:
            automl_settings_obj.label_column_name = dataprep_json_obj.get('label', None)
            logger.info('Set label_column_name')

    if automl_settings_obj.enable_stack_ensembling is True or automl_settings_obj.enable_ensembling is True:
        logger.warning('The training data is large. Ensembling is not available for this run.')
        automl_settings_obj.enable_stack_ensembling = False
        automl_settings_obj.enable_ensembling = False
