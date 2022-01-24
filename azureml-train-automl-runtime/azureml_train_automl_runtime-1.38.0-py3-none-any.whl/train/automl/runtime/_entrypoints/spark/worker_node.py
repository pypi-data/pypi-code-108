# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class that runs automl run on ADB worker node."""
import datetime
import json
import logging
import os
import uuid
from typing import cast, Any, Optional, Dict

import gc
from azureml._base_sdk_common.service_discovery import HISTORY_SERVICE_ENDPOINT_KEY
from azureml._restclient.jasmine_client import JasmineClient
from azureml._restclient.service_context import ServiceContext
from azureml._restclient.exceptions import ServiceException
from azureml._restclient.models import IterationTask
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.constants import PreparationRunTypeConstants
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.core import Run, Datastore
from azureml.core.authentication import AzureMLTokenAuthentication
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml._common.exceptions import AzureMLException
from azureml.data.constants import WORKSPACE_BLOB_DATASTORE

from azureml.automl.core import logging_utilities
from azureml.automl.core._logging import log_server
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.core.shared import logging_utilities as log_utils
from azureml.automl.core.shared._diagnostics.error_strings import AutoMLErrorStrings
from azureml.automl.core.shared.exceptions import CacheException, ErrorTypes
from azureml.automl.core.systemusage_telemetry import SystemResourceUsageTelemetryFactory
from azureml.automl.runtime import fit_pipeline as fit_pipeline_helper
from azureml.automl.runtime._runtime_params import ExperimentControlSettings, ExperimentDataSettings
from azureml.automl.runtime.automl_pipeline import AutoMLPipeline
from azureml.automl.runtime.featurizer.transformer.featurization_utilities import skip_featurization
from azureml.automl.runtime.faults_verifier import VerifierManager
from azureml.automl.runtime.fit_output import FitOutput
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.train.automl._automl_feature_config_manager import AutoMLFeatureConfigManager
from azureml.train.automl._amlloguploader import _AMLLogUploader
from azureml.train.automl import _logging   # type: ignore
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl._azure_experiment_observer import AzureExperimentObserver
from azureml.train.automl._constants_azureml import CodePaths
from azureml.train.automl._execute_with_retry import ExecuteWithRetry
from azureml.train.automl.constants import ComputeTargets
from azureml.train.automl.runtime._automl_job_phases import (
    FeaturizationPhase, ExperimentPreparationPhase, ModelExplainPhase, TrainingIterationPhase, TrainingIterationParams
)
from azureml.train.automl.runtime._automl_model_explain import ModelExplainParams
from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext
from azureml.train.automl.runtime._cachestorefactory import CacheStoreFactory
from azureml.train.automl.runtime._entrypoints.utils import (common as entrypoint_util,
                                                             featurization as featurization_entrypoint_util,
                                                             training as training_entrypoint_util)
from azureml.train.automl.runtime.run import AutoMLRun
from azureml.train.automl.utilities import _get_package_version


MAX_RETRY_COUNT_ON_EXCEPTION = 5
BACK_OFF_FACTOR = 2
MAX_RETRY_COUNT_DURING_SETUP = 10000
MAX_WAIT_IN_SECONDS = 300
SLEEP_TIME = 10


logger = logging.getLogger(__name__)


def run_setup_and_train_iterations(input_params):
    adb_experiment = _get_adb_experiment(input_params)
    adb_experiment.run()


def run_model_explain_iteration(input_params):
    adb_experiment = _get_adb_experiment(input_params)
    adb_experiment.run_explain()


def _get_adb_experiment(input_params):
    """
    Read run configuration, get next pipeline, and call fit iteration.

    :param input_params: List of input parameters.
    :type input_params: list
    :return:
    :rtype: None
    """
    worker_id = input_params[0]
    run_context = input_params[1]
    subscription_id = run_context.get('subscription_id', None)
    resource_group = run_context.get('resource_group', None)
    workspace_name = run_context.get('workspace_name', None)
    location = run_context.get('location', None)
    aml_token = run_context.get('aml_token', None)
    aml_token_expiry = run_context.get('aml_token_expiry', None)
    experiment_name = run_context.get('experiment_name', None)
    experiment_id = run_context.get('experiment_id', None)
    parent_run_id = run_context.get('parent_run_id', None)
    service_url = run_context.get('service_url', None)
    discovery_url = run_context.get('discovery_url', None)
    dataprep_json = run_context.get('dataprep_json', None)
    automl_settings_str = run_context.get('automl_settings_str', None)
    _set_env_variables(subscription_id,
                       resource_group,
                       workspace_name,
                       experiment_name,
                       aml_token,
                       aml_token_expiry,
                       service_url,
                       discovery_url)

    adb_experiment = _AdbAutomlExperiment(parent_run_id,
                                          subscription_id,
                                          resource_group,
                                          workspace_name,
                                          experiment_name,
                                          experiment_id,
                                          aml_token,
                                          aml_token_expiry,
                                          service_url,
                                          location,
                                          automl_settings_str,
                                          dataprep_json,
                                          worker_id,
                                          discovery_url)
    return adb_experiment


def _set_env_variables(subscription_id, resource_group, workspace_name, experiment_name,
                       aml_token, aml_token_expiry, service_url, discovery_url):
    df_value_list = [(subscription_id, "subscription_id"),
                     (resource_group, "resource_group"),
                     (workspace_name, "workspace_name"),
                     (experiment_name, "experiment_name"),
                     (aml_token, "aml_token"),
                     (aml_token_expiry, "aml_token_expiry"),
                     (service_url, "service_url")]
    for var, var_name in df_value_list:
        Validation.validate_value(var, var_name)

    os.environ["AZUREML_ARM_SUBSCRIPTION"] = subscription_id
    os.environ["AZUREML_ARM_RESOURCEGROUP"] = resource_group
    os.environ["AZUREML_ARM_WORKSPACE_NAME"] = workspace_name
    os.environ["AZUREML_ARM_PROJECT_NAME"] = experiment_name
    os.environ["AZUREML_RUN_TOKEN"] = aml_token
    os.environ["AZUREML_RUN_TOKEN_EXPIRY"] = str(aml_token_expiry)
    os.environ["AZUREML_SERVICE_ENDPOINT"] = service_url
    os.environ["AZUREML_DISCOVERY_SERVICE_ENDPOINT"] = discovery_url


def log_message(logging_level=logging.INFO, parent_run_id=None, worker_id=None, message=None):
    """
    Use to log messages.

    :param logging_level: The logging level to use.
    :type logging_level: int
    :param parent_run_id: The associated parent run ID.
    :type parent_run_id: str
    :param worker_id: The associated worker node ID.
    :type worker_id: str
    :param message: The associated message.
    :type message: str
    :return:
    :rtype: None
    """
    if logging_level == logging.ERROR:
        logger.error("{0}, {1}, {2}".format(parent_run_id, worker_id, message))
    elif logging_level == logging.DEBUG:
        logger.debug("{0}, {1}, {2}".format(parent_run_id, worker_id, message))
    elif logging_level == logging.WARNING:
        logger.warning("{0}, {1}, {2}".format(parent_run_id, worker_id, message))
    else:
        logger.info("{0}, {1}, {2}".format(parent_run_id, worker_id, message))


class _AdbAutomlExperiment:

    DATASET_CACHED_KEY = 'dataset_cached_object'
    CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA = '_CACHE_STORE_KEY_ONNX_CONVERTER_INIT_METADATA_'

    def __init__(self,
                 parent_run_id,
                 subscription_id,
                 resource_group,
                 workspace_name,
                 experiment_name,
                 experiment_id,
                 aml_token,
                 aml_token_expiry,
                 service_url,
                 location,
                 automl_settings_str,
                 dataprep_json,
                 worker_id,
                 discovery_url):
        self.parent_run_id = parent_run_id
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.workspace_name = workspace_name
        self.experiment_name = experiment_name
        self.experiment_id = experiment_id
        self.aml_token = aml_token
        self.aml_token_expiry = aml_token_expiry
        self.service_url = service_url
        self.location = location
        self.worker_id = worker_id
        self.automl_settings_str = automl_settings_str
        self.discovery_url = discovery_url

        os.environ["AZUREML_RUN_TOKEN"] = self.aml_token
        os.environ["AZUREML_RUN_TOKEN_EXPIRY"] = str(self.aml_token_expiry)

        Contract.assert_value(automl_settings_str, "automl_settings_str")
        self.automl_settings = AzureAutoMLSettings(
            self._rehydrate_experiment(), **json.loads(self.automl_settings_str))

        # Don't reuse path from user's local machine for ADB runs
        self.automl_settings.path = os.getcwd()

        _logging.set_run_custom_dimensions(automl_settings=self.automl_settings,
                                           parent_run_id=self.parent_run_id,
                                           child_run_id=None,
                                           code_path=CodePaths.DATABRICKS)

        self._usage_telemetry = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry()
        self._usage_telemetry.start()

        Contract.assert_value(dataprep_json, "dataprep_json")
        self.dataprep_json = dataprep_json
        self.jasmine_client_exception_count = 0

        try:
            # Note that this is due to known issue in shap library
            # Until that issue is fixed this is temporary mitigation specific
            # to AzureDatabricks.
            import matplotlib as mpl
            mpl.use('AGG')
        except Exception as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            self.log_message(message="Failed set the matplot backend", logging_level=logging.ERROR)

    def _should_retry(self, output, exception, current_retry):
        pipeline_dto = output
        if pipeline_dto is not None:
            # reset exception counter since we were able to establish connnection
            self.jasmine_client_exception_count = 0
            should_retry = ((pipeline_dto.pipeline_spec is None or pipeline_dto.pipeline_spec == '') and
                            not pipeline_dto.is_experiment_over)
            should_retry = (should_retry and
                            ((pipeline_dto.childrun_id is not None or pipeline_dto.childrun_id == '') and
                             not self._is_special_run(pipeline_dto.childrun_id)))
            return (should_retry, BACK_OFF_FACTOR)
        elif exception is not None:
            self.jasmine_client_exception_count += 1
            if self.jasmine_client_exception_count == MAX_RETRY_COUNT_ON_EXCEPTION:
                return (False, BACK_OFF_FACTOR)

            return (True, BACK_OFF_FACTOR)

        return (False, BACK_OFF_FACTOR)

    def _is_special_run(self, run_id):
        return run_id.endswith("setup") or run_id.endswith("ModelExplain")

    def _get_next_pipeline(self):
        jasmine_client = self._create_client()
        pipeline_dto = jasmine_client.get_next_pipeline(
            self.parent_run_id, self.worker_id)
        return pipeline_dto

    def log_message(self, message, logging_level=logging.DEBUG):
        log_message(logging_level=logging_level,
                    parent_run_id=self.parent_run_id,
                    worker_id=self.worker_id,
                    message=message)

    def run_explain(self):
        parent_run_id = self.parent_run_id
        worker_id = self.worker_id
        log_message(parent_run_id=parent_run_id, worker_id=worker_id,
                    message="Starting model explain run on worker node...")

        try:
            self._model_explain_iteration()
        except Exception as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            log_message(logging_level=logging.ERROR, parent_run_id=parent_run_id,
                        worker_id=worker_id, message='Model explain failed')
            raise
        log_message(parent_run_id=parent_run_id, worker_id=worker_id,
                    message="Finished model_explain run on worker node.")

    def run(self):

        parent_run_id = self.parent_run_id
        worker_id = self.worker_id
        log_message(parent_run_id=parent_run_id, worker_id=worker_id,
                    message="Starting experiment run on worker node...")

        try:
            while True:
                execute_with_retry = ExecuteWithRetry(
                    MAX_RETRY_COUNT_DURING_SETUP,
                    MAX_WAIT_IN_SECONDS,
                    self._should_retry,
                    self.log_message,
                    "jasmine_client.get_next_pipeline()")
                pipeline_dto = execute_with_retry.execute(
                    self._get_next_pipeline,
                    func_name="get_next_pipeline")
                if pipeline_dto.is_experiment_over:
                    log_message(parent_run_id=parent_run_id, worker_id=worker_id,
                                message="Experiment finished.")
                    break
                child_run_id = pipeline_dto.childrun_id
                with log_server.new_log_context(run_id=child_run_id):
                    os.environ["AZUREML_RUN_ID"] = child_run_id
                    self.execute_pipeline(pipeline_dto, child_run_id)
        except Exception as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            log_message(logging_level=logging.ERROR, parent_run_id=parent_run_id,
                        worker_id=worker_id, message='Spark experiment failed')
            raise
        finally:
            try:
                parent_run = self._rehydrate_run(parent_run_id)
                if self.automl_settings.debug_log:
                    filename, file_extension = os.path.splitext(self.automl_settings.debug_log)
                    if os.path.exists(self.automl_settings.debug_log):
                        if not self.automl_settings.debug_log.startswith("/dbfs"):
                            formatted_file_name = "logs/{0}_{1}_{2}{3}".format(
                                filename, str(worker_id),
                                datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%SZ"),
                                file_extension)

                            parent_run.upload_file(formatted_file_name, self.automl_settings.debug_log)
            except Exception as e:
                log_utils.log_traceback(e, logger, is_critical=False)
                log_message(logging_level=logging.WARNING, parent_run_id=parent_run_id,
                            worker_id=worker_id, message="Upload to parent run failed")

        log_message(parent_run_id=parent_run_id, worker_id=worker_id,
                    message="Finished experiment run on worker node.")

    def _rehydrate_experiment(self) -> Experiment:
        auth = AzureMLTokenAuthentication.create(self.aml_token,
                                                 AzureMLTokenAuthentication._convert_to_datetime(
                                                     self.aml_token_expiry),
                                                 self.service_url,
                                                 self.subscription_id,
                                                 self.resource_group,
                                                 self.workspace_name,
                                                 self.experiment_name,
                                                 self.parent_run_id)
        workspace = Workspace(self.subscription_id,
                              self.resource_group, self.workspace_name,
                              auth=auth,
                              _location=self.location,
                              _disable_service_check=True)
        experiment = Experiment(workspace, self.experiment_name)
        return experiment

    def _rehydrate_run(self, run_id: str) -> Run:
        return Run(self._rehydrate_experiment(), run_id)

    def _setup_iteration(self, verifier: VerifierManager, current_run: Run, run_id: str) -> None:
        """
        Code for running experiment preparation and featurization phases.
        """
        parent_run = self._rehydrate_run(self.parent_run_id)
        experiment_observer = AzureExperimentObserver(parent_run)
        raw_experiment_data, feature_config_manager = \
            featurization_entrypoint_util.initialize_data(current_run, "setup", self.automl_settings,
                                                          None, self.dataprep_json, None,
                                                          parent_run.id, verifier)
        cache_store = self._get_cache_store()
        expr_store = ExperimentStore(cache_store, read_only=False)
        logger.info('Using {} for caching transformed data.'.format(type(cache_store).__name__))

        experiment_observer = AzureExperimentObserver(parent_run)
        featurization_entrypoint_util.cache_onnx_init_metadata(cache_store, raw_experiment_data,
                                                               self.parent_run_id)
        try:
            feature_sweeped_state_container = ExperimentPreparationPhase.run(
                parent_run_id=self.parent_run_id,
                automl_settings=self.automl_settings,
                cache_store=cache_store,
                current_run=current_run,
                experiment_observer=experiment_observer,
                feature_config_manager=feature_config_manager,
                raw_experiment_data=raw_experiment_data,
                validate_training_data=True,
                verifier=verifier
            )

            FeaturizationPhase.run(
                parent_run_id=self.parent_run_id,
                automl_settings=self.automl_settings,
                cache_store=cache_store,
                current_run=current_run,
                experiment_observer=experiment_observer,
                feature_config_manager=feature_config_manager,
                feature_sweeped_state_container=feature_sweeped_state_container,
                raw_experiment_data=raw_experiment_data,
                verifier=verifier
            )

            # Cache the experiment data irrespective of whether featurization was turned off or not.
            # We save the hard work done to transform the data
            # on the Azure Blob Store cache / local disk, from where other worker nodes can download from.
            expr_store.unload()
        finally:
            # Reset the experiment store so it can be re-created with read_only=True for training iterations.
            ExperimentStore.reset()

        featurization_entrypoint_util._report_featurization_complete(experiment_observer, self.parent_run_id)

        if verifier is not None:
            parent_run_context = AzureAutoMLRunContext(parent_run, False)
            verifier.write_result_file(parent_run_context)

        # Setup's finished. Eagerly clean up the input and/or featurized data.
        # The model iteration workers will load the cached data
        self._gc_object(raw_experiment_data)
        logger.info('Setup iteration "{}" finished successfully.'.format(run_id))

    def _train_iteration(self,
                         verifier: VerifierManager,
                         current_run: Run,
                         pkg_ver: str,
                         pipeline_dto: IterationTask,
                         run_id: str) -> FitOutput:
        """
        Runs one training child iteration using the given pipeline spec for the run.
        """
        logger.info('Beginning fit iteration: {}.'.format(run_id))
        pipeline_id = pipeline_dto.pipeline_id
        cache_store = self._get_cache_store()
        expr_store = ExperimentStore(cache_store, read_only=True)
        expr_store.load()
        if self.automl_settings.enable_streaming:
            entrypoint_util.modify_settings_for_streaming(self.automl_settings, self.dataprep_json)
        onnx_cvt = training_entrypoint_util.load_onnx_converter(self.automl_settings, cache_store, self.parent_run_id)

        automl_run_context = AzureAutoMLRunContext(Run.get_context(), is_adb_run=True)
        parent_run = self._rehydrate_run(self.parent_run_id)
        training_percent = int(pipeline_dto.training_percent or 100)

        automl_run_context.set_local(False)
        try:
            result = TrainingIterationPhase.run(
                automl_parent_run=parent_run,
                automl_run_context=automl_run_context,
                training_iteration_params=TrainingIterationParams(self.automl_settings),
                onnx_cvt=onnx_cvt,
                pipeline_id=pipeline_id,
                pipeline_spec=pipeline_dto.pipeline_spec,
                training_percent=training_percent,
            )
        finally:
            ExperimentStore.reset()

        return result

    def _model_explain_iteration(self) -> None:
        """
        Compute best run or on demand model explanation.
        """
        log_message(parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                    message="Model explain for best run starts.")
        # Rehydrate the parent run
        parent_run = AutoMLRun(self._rehydrate_experiment(), self.parent_run_id)
        # Recover the dataset from cache store
        cache_store = self._get_cache_store()

        try:
            expr_store = ExperimentStore(cache_store, read_only=True)
            expr_store.load()
            # Perform model explanations for best run
            ModelExplainPhase.explain_best_run(
                parent_run,
                ModelExplainParams(self.automl_settings),
                ComputeTargets.ADB
            )
        finally:
            ExperimentStore.reset()

        log_message(parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                    message="Model explain for best run ends.")

    def execute_pipeline(self, pipeline_dto: IterationTask, run_id: str) -> None:
        """
        Fit iteration method.

        :param pipeline_dto: Pipeline details to fit.
        :type pipeline_dto: PipelineDto
        :param run_id: run id.
        :type run_id: string
        """
        run_id = pipeline_dto.childrun_id
        pipeline_id = pipeline_dto.pipeline_id

        """
        # TODO: Fix pipeline spec logging (#438111)
        log_message(parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                    message="Received pipeline: {0} for run id '{1}'".format(pipeline_dto.pipeline_spec, run_id))
        """
        logger.info('Received pipeline ID {}'.format(pipeline_id))

        verifier = VerifierManager()

        # This is due to token expiry issue
        current_run = self._rehydrate_run(run_id)

        result = None   # type: Optional[FitOutput]
        with _AMLLogUploader(current_run, self.worker_id):
            try:
                log_message(parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="{0}: Starting childrun...".format(run_id))
                self._execute_with_retry_ignored(current_run.start)

                pkg_ver = _get_package_version()
                if run_id.endswith("setup"):
                    self._setup_iteration(verifier, current_run, run_id)
                else:
                    result = self._train_iteration(verifier, current_run, pkg_ver,
                                                   pipeline_dto, run_id)

                    if result.errors:
                        err_type = next(iter(result.errors))
                        exception_info = result.errors[err_type]
                        exception_obj = cast(BaseException, exception_info['exception'])
                        log_message(logging_level=logging.ERROR,
                                    parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                                    message="Exception raised")

                        if exception_info['is_critical']:
                            raise exception_obj.with_traceback(exception_obj.__traceback__)

                    score = result.score
                    duration = result.actual_time
                    log_message(parent_run_id=self.parent_run_id,
                                worker_id=self.worker_id, message="Score: {0}".format(score))
                    log_message(parent_run_id=self.parent_run_id,
                                worker_id=self.worker_id, message="Duration: {0}".format(duration))

                self._execute_with_retry_ignored(current_run.complete)
                log_message(parent_run_id=self.parent_run_id, worker_id=self.worker_id,
                            message="{0}: Fit iteration completed successfully.".format(run_id))

            except Exception as e:
                if result is not None and result._hit_experiment_timeout:
                    run_lifecycle_utilities.cancel_run(
                        current_run,
                        warning_string=AutoMLErrorStrings.EXPERIMENT_TIMED_OUT
                    )
                    return
                log_utils.log_traceback(e, logger, is_critical=False)
                log_message(logging_level=logging.ERROR, parent_run_id=self.parent_run_id,
                            worker_id=self.worker_id, message='{}: Iteration failed'.format(run_id))
                if current_run is not None:
                    run_lifecycle_utilities.fail_run(current_run, e)
                if run_id.endswith("setup"):
                    try:
                        error_message = str({'exception': e})
                        current_run.tag("errors", error_message)

                        errors = {
                            'errors': error_message,
                            'error_code': getattr(e, 'error_code', ErrorTypes.Unclassified),
                            'failure_reason': getattr(e, 'error_type', ErrorTypes.Unclassified)
                        }
                        current_run.add_properties(errors)

                    except AzureMLException as ae:
                        log_utils.log_traceback(ae, logger, is_critical=False)
                        self.log_message(logging_level=logging.ERROR,
                                         message="Failed to add 'errors' properties to run due to exception")
                        raise

    def _execute_with_retry_ignored(self, func: Any) -> None:
        try:
            func()
        except ServiceException as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            log_message(logging_level=logging.ERROR,
                        parent_run_id=self.parent_run_id,
                        worker_id=self.worker_id,
                        message="Exception occurred while making call to RunHistory")
            if e.status_code == 400 and " is already set." in e.message:
                pass
            else:
                raise

    def _create_client(self):
        auth = AzureMLTokenAuthentication.create(self.aml_token,
                                                 AzureMLTokenAuthentication._convert_to_datetime(
                                                     self.aml_token_expiry),
                                                 self.service_url,
                                                 self.subscription_id,
                                                 self.resource_group,
                                                 self.workspace_name,
                                                 self.experiment_name,
                                                 self.parent_run_id)
        os.environ[HISTORY_SERVICE_ENDPOINT_KEY] = self.service_url
        # Discovery url will not be same as history service end point
        # Based on workspace vnet, workspace will have workspace dependent discovery end point
        os.environ["AZUREML_DISCOVERY_SERVICE_ENDPOINT"] = self.discovery_url
        service_context = ServiceContext(self.subscription_id,
                                         self.resource_group,
                                         self.workspace_name,
                                         None,
                                         self.discovery_url,
                                         auth)
        return JasmineClient(service_context=service_context,
                             experiment_name=self.experiment_name,
                             experiment_id=self.experiment_id,
                             user_agent="JasmineClient")

    def _get_cache_store(self):
        data_store = self._get_data_store()

        temp_dir = self.parent_run_id if self.parent_run_id else str(uuid.uuid4())

        return CacheStoreFactory.get_cache_store(
            temp_location=os.path.join(self.automl_settings.path, temp_dir),
            run_target='adb',
            run_id=self.parent_run_id,
            data_store=data_store
        )

    def _get_data_store(self):
        try:
            experiment = self._rehydrate_experiment()
            return Datastore.get(experiment.workspace, WORKSPACE_BLOB_DATASTORE)
        except Exception as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            log_message(logging_level=logging.ERROR, parent_run_id=self.parent_run_id,
                        worker_id=self.worker_id,
                        message="No default data store found")
            return None

    def __del__(self):
        """
        Clean up AutoML loggers and close files.
        """
        if self._usage_telemetry is not None:
            self._usage_telemetry.stop()

    def _gc_object(self, obj: Any) -> None:
        if obj is not None:
            del obj
            gc.collect()
