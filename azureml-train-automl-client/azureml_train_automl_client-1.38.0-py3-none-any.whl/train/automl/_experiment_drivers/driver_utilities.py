# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility functions for use by client code."""
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union, cast

from azureml._common._error_definition import AzureMLError
from azureml._common.exceptions import AzureMLException
from azureml._restclient.constants import ONE_MB, SNAPSHOT_MAX_FILES, SNAPSHOT_MAX_SIZE_BYTES, RunStatus
from azureml._restclient.models import LocalRunGetNextTaskBatchInput, LocalRunGetNextTaskInput, MiroProxyInput
from azureml._restclient.models.create_parent_run import CreateParentRun
from azureml._restclient.models.run_dto import RunDto
from azureml._tracing._tracer_factory import get_tracer
from azureml.core import Experiment, Run
from azureml.core._serialization_utils import _serialize_to_dict
from azureml.core.runconfig import RunConfiguration
from azureml.dataprep import Dataflow
from azureml.exceptions import ServiceException as AzureMLServiceException
from azureml.exceptions import SnapshotException
from msrest.exceptions import ClientRequestError

from azureml.automl.core import dataprep_utilities, dataset_utilities, package_utilities
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.constants import RunHistoryEnvironmentVariableNames
from azureml.automl.core.shared import import_utilities, logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AutoMLInternal,
    ExecutionFailure,
    InvalidArgumentType,
    InvalidArgumentWithSupportedValues,
    RuntimeModuleDependencyMissing,
    SnapshotLimitExceeded,
)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.constants import TelemetryConstants
from azureml.automl.core.shared.exceptions import (
    AutoMLException,
    ClientException,
    ConfigException,
    ValidationException,
)
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from .. import _logging, constants
from .._azure_experiment_state import AzureExperimentState
from .._constants_azureml import CodePaths, Properties
from .._environment_utilities import modify_run_configuration
from ..exceptions import FetchNextIterationException
from ..run import AutoMLRun
from ..utilities import _InternalComputeTypes

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


def create_and_validate_parent_run_dto(
    experiment_state,
    target,
    training_data,
    validation_data,
    X,
    y,
    sample_weight,
    X_valid,
    y_valid,
    sample_weight_valid,
    cv_splits_indices,
    parent_run_id=None,
    test_data=None,
):
    """Create the parent DTO and validate it by invoking validation service in JOS."""
    dataprep_json = serialize_datasets_to_json(X, X_valid, y, y_valid, sample_weight, sample_weight_valid,
                                               training_data, validation_data, test_data, cv_splits_indices)

    parent_run_dto = create_parent_run_dto(experiment_state, target, dataprep_json, parent_run_id)

    validate_input(experiment_state, parent_run_dto)

    return parent_run_dto


def serialize_datasets_to_json(
        X: Optional[Dataflow] = None,
        X_valid: Optional[Dataflow] = None,
        y: Optional[Dataflow] = None,
        y_valid: Optional[Dataflow] = None,
        sample_weight: Optional[Dataflow] = None,
        sample_weight_valid: Optional[Dataflow] = None,
        training_data: Optional[Dataflow] = None,
        validation_data: Optional[Dataflow] = None,
        test_data: Optional[Dataflow] = None,
        cv_splits_indices: Optional[Dataflow] = None
) -> Optional[str]:
    dataprep_json = None    # type: Optional[str]
    if training_data is not None:
        if isinstance(training_data, Dataflow):
            dataprep_json = dataprep_utilities.get_dataprep_json_dataset(
                training_data=training_data, validation_data=validation_data, test_data=test_data
            )
        else:
            dataprep_json = dataset_utilities.get_datasets_json(
                training_data=training_data, validation_data=validation_data, test_data=test_data
            )
    else:
        dataprep_json = dataprep_utilities.get_dataprep_json(
            X=X,
            y=y,
            sample_weight=sample_weight,
            X_valid=X_valid,
            y_valid=y_valid,
            sample_weight_valid=sample_weight_valid,
            cv_splits_indices=cv_splits_indices,
        )
    if dataprep_json is not None:
        # escape quotations in json_str before sending to jasmine
        dataprep_json = dataprep_json.replace("\\", "\\\\").replace('"', '\\"')
    return dataprep_json


def validate_input(experiment_state: AzureExperimentState, parent_run_dto: CreateParentRun) -> None:
    logger.info("Start data validation.")
    validation_results = None
    with tracer.start_as_current_span(
        TelemetryConstants.SPAN_FORMATTING.format(
            TelemetryConstants.COMPONENT_NAME, TelemetryConstants.DATA_VALIDATION
        ),
        user_facing_name=TelemetryConstants.DATA_VALIDATION_USER_FACING,
    ):
        try:
            validation_results = experiment_state.jasmine_client.post_validate_service(parent_run_dto)
            # We get an empty response (HTTP 204) when the validation succeeds,
            # a HTTP 200 with an error response is raised otherwise
            if validation_results is None:
                logger.info("Validation service found the data has no errors.")
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            # Any other validation related exception won't fail the experiment.
            logger.warning("Validation service meet exceptions, continue training now.")

    if (
        validation_results is not None and
            len(validation_results.error.details) > 0 and
            any([d.code != "UpstreamSystem" for d in validation_results.error.details])
    ):
        # If validation service meets error thrown by the upstream service, the run will continue.
        experiment_state.console_writer.println("The validation results are as follows:")
        errors = []
        for result in validation_results.error.details:
            if result.code != "UpstreamSystem":
                experiment_state.console_writer.println(result.message)
                errors.append(result.message)
        msg = "Validation error(s): {}".format(validation_results.error.details)
        raise ValidationException._with_error(AzureMLError.create(
            ExecutionFailure, operation_name="data/settings validation", error_details=msg)
        )


def create_parent_run_dto(
    experiment_state: AzureExperimentState,
    target: Optional[Union[RunConfiguration, str]],
    dataprep_json: Optional[str] = None,
    parent_run_id: Optional[str] = None,
) -> CreateParentRun:
    """
    Create CreateParentRun.

    :param target: run configuration
    :type target: RunConfiguration or str
    :param dataprep_json: dataprep json string
    :type dataprep_json: str
    :param parent_run_id: Parent run id.
    :return: CreateParentRun to be sent to Jasmine
    :rtype: CreateParentRun
    """

    # Remove path when creating the DTO
    settings_dict = experiment_state.automl_settings.as_serializable_dict()
    settings_dict["path"] = None

    parent_run_dto = CreateParentRun(
        target=target,
        run_source=experiment_state.automl_settings.run_source,
        run_type="automl",
        num_iterations=experiment_state.automl_settings.iterations,
        training_type=None,  # use self.training_type when jasmine supports it
        acquisition_function=None,
        metrics=["accuracy"],
        primary_metric=experiment_state.automl_settings.primary_metric,
        train_split=experiment_state.automl_settings.validation_size,
        acquisition_parameter=0.0,
        num_cross_validation=experiment_state.automl_settings.n_cross_validations,
        aml_settings_json_string=json.dumps(settings_dict),
        data_prep_json_string=dataprep_json,
        enable_subsampling=experiment_state.automl_settings.enable_subsampling,
        properties=get_current_run_properties_to_update(experiment_state),
        scenario=experiment_state.automl_settings.scenario,
        environment_label=experiment_state.automl_settings.environment_label,
        parent_run_id=parent_run_id,
    )
    return parent_run_dto


def get_current_run_properties_to_update(experiment_state: AzureExperimentState) -> Dict[str, str]:
    """Get properties to update on the current run object."""
    # TODO: Remove with task 416022
    # This property is to temporarily fix: 362194.
    # It should be removed promptly.
    task = experiment_state.automl_settings.task_type
    if experiment_state.automl_settings.is_timeseries:
        task = constants.Tasks.FORECASTING
    display_task_type_property = {Properties.DISPLAY_TASK_TYPE_PROPERTY: task}

    # Log the AzureML packages currently installed on the local machine to the given run.
    user_sdk_dependencies_property = {
        Properties.SDK_DEPENDENCIES_PROPERTY: json.dumps(package_utilities.get_sdk_dependencies())
    }

    # Make sure to batch all relevant properties in this single call in-order to avoid multiple network trips to RH
    result = {**display_task_type_property, **user_sdk_dependencies_property}
    return result


def check_package_compatibilities(experiment_state: AzureExperimentState, is_managed_run: bool = False) -> None:
    """
    Check package compatibilities and raise exceptions otherwise.

    :param is_managed_run: Whether the current run is a managed run.
    :raises: `azureml.automl.core.shared.exceptions.RequiredDependencyMissingOrIncompatibleException`
    in case of un-managed runs.
    """
    if experiment_state.automl_settings._ignore_package_version_incompatibilities:
        return
    try:
        is_databricks_run = (
            experiment_state.automl_settings.azure_service == _InternalComputeTypes.DATABRICKS
        )
        package_utilities._get_package_incompatibilities(
            packages=package_utilities.AUTOML_PACKAGES,
            ignored_dependencies=package_utilities._PACKAGES_TO_IGNORE_VERSIONS,
            is_databricks_run=is_databricks_run,
        )
    except ValidationException as ex:
        if is_managed_run:
            # VSO: 1049118
            message = ex.pii_free_msg
            logger.error("Found package mismatch for local managed environment. {}".format(message))
        else:
            raise


def fail_parent_run(experiment_state: AzureExperimentState,
                    error_details: BaseException, is_aml_compute: bool) -> None:
    """
    Mark the parent run as 'Failed'. Additionally, a notification is sent to JOS (which may log run terminal
    details in the service side telemetry)

    This is a No-Op if there is no parent run created yet.
    """
    logging_utilities.log_traceback(error_details, logger)

    if experiment_state.current_run is None:
        logger.info("No parent run to fail")
        return

    logger.error("Run {} failed with exception of type: {}".format(
        str(experiment_state.parent_run_id), type(error_details)))

    try:
        # If the run is already in a terminal state, don't update the status again
        current_run_status = experiment_state.current_run.get_status()
        if current_run_status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELED]:
            logger.warning('Cannot fail the current run since it is already in a terminal state of [{}].'.
                           format(current_run_status))
            return
        if experiment_state.current_run is not None:
            run_lifecycle_utilities.fail_run(
                experiment_state.current_run, error_details, is_aml_compute=is_aml_compute, update_run_properties=True
            )
        if experiment_state.jasmine_client is not None and experiment_state.parent_run_id is not None:
            logger.info(
                "Setting Run {} status to: {}".format(
                    str(experiment_state.parent_run_id), constants.RunState.FAIL_RUN)
            )
            experiment_state.jasmine_client.set_parent_run_status(
                experiment_state.parent_run_id, constants.RunState.FAIL_RUN
            )
    except (AzureMLException, AzureMLServiceException, ClientRequestError) as e:
        logger.error("Encountered an error while failing the parent run. Exception type: {}".
                     format(e.__class__.__name__))
        logging_utilities.log_traceback(error_details, logger)
        raise
    except Exception as e:
        logger.error("Encountered an error while failing the parent run. Exception type: {}".
                     format(e.__class__.__name__))
        raise ClientException.from_exception(e, has_pii=True).with_generic_msg(
            "Error occurred when trying to set parent run status."
        )


def start_remote_run(experiment_state: AzureExperimentState, run_configuration: Union[str, RunConfiguration]) -> None:
    """
    Create the parent run and submit the snapshot to JOS.

    :param run_configuration: Run configuration for this run, either user provided or system-generated.
    :param X: X input data. Not compatible with training_data.
    :param y: y input data. Not compatible with training_data.
    :param sample_weight: Sample weights for the data.
    :param X_valid: X validation data.
    :param y_valid: y validation data.
    :param sample_weight_valid: Sample weights for the validation data.
    :param cv_splits_indices: Indices of all the cross folds.
    :param training_data: Training data. Not compatible with X and y.
    :param validation_data: Validation data. Not compatible with X and y.
    :param test_data: Test data. Not compatible with X and y.
    :return:
    """
    if isinstance(run_configuration, str):
        run_configuration = RunConfiguration.load(experiment_state.automl_settings.path, run_configuration)

    try:
        snapshot_id = None
        if experiment_state.user_script is not None:
            # A snapshot is only needed if the user is using a custom data script
            snapshot_id = take_snapshot(experiment_state)
            Contract.assert_non_empty(snapshot_id, "snapshot_id", reference_code="_start_remote_run", log_safe=True)

        definition = {
            "Configuration": _serialize_to_dict(run_configuration)
        }

        definition["Configuration"]["environment"]["python"]["condaDependencies"] = \
            json.loads(json.dumps(run_configuration.environment.python.conda_dependencies._conda_dependencies))

        logger.info("Starting a snapshot run (snapshot_id : {0})".format(snapshot_id))
        experiment_state.jasmine_client.post_remote_jasmine_snapshot_run(
            experiment_state.parent_run_id, definition, snapshot_id
        )
    except (AzureMLException, AzureMLServiceException) as e:
        logging_utilities.log_traceback(e, logger)
        raise
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        raise ClientException.from_exception(e, target="AzureAutoMLClientfitremotecore").with_generic_msg(
            "Error occurred trying to run snapshot run."
        )


def create_remote_parent_run(experiment_state, run_config, X=None, y=None, sample_weight=None,
                             X_valid=None, y_valid=None, sample_weight_valid=None, cv_splits_indices=None,
                             training_data=None, validation_data=None, test_data=None):
    if run_config is None:
        run_config = RunConfiguration()
    elif isinstance(run_config, str):
        run_config = RunConfiguration.load(experiment_state.automl_settings.path, run_config)
    run_config = modify_run_configuration(experiment_state.automl_settings, run_config, logger)

    # Uncomment to fall back to curated envs for changing environment behavior
    # run_config_object = modify_run_configuration_curated(self.automl_settings,
    #                                                      run_config_object,
    #                                                      self.experiment.workspace,
    #                                                      logger)

    parent_run_dto = create_and_validate_parent_run_dto(
        experiment_state=experiment_state,
        target=run_config.target,
        training_data=training_data,
        validation_data=validation_data,
        X=X,
        y=y,
        sample_weight=sample_weight,
        X_valid=X_valid,
        y_valid=y_valid,
        sample_weight_valid=sample_weight_valid,
        cv_splits_indices=cv_splits_indices,
        test_data=test_data,
    )

    try:
        logger.info("Start creating parent run.")
        experiment_state.parent_run_id = experiment_state.jasmine_client.post_parent_run(parent_run_dto)
        # Populating the logging custom dimensions with the parent run id,
        # so that AppInsights querying gets easier.
        _logging.set_run_custom_dimensions(
            automl_settings=experiment_state.automl_settings,
            parent_run_id=experiment_state.parent_run_id,
            child_run_id=None,
            code_path=CodePaths.REMOTE
        )
    except (AzureMLException, AzureMLServiceException):
        raise
    except Exception as e:
        raise ClientException.from_exception(e, target="__create_remote_parent_run").with_generic_msg(
            "Error occurred when trying to create new parent run in AutoML service."
        )

    if experiment_state.user_script:
        logger.info("[ParentRunID:{}] Remote run using user script.".format(experiment_state.parent_run_id))
    else:
        logger.info("[ParentRunID:{}] Remote run using input X and y.".format(experiment_state.parent_run_id))

    if experiment_state.current_run is None:
        experiment_state.current_run = AutoMLRun(
            experiment_state.experiment,
            experiment_state.parent_run_id,
            host=experiment_state.automl_settings.service_url,
        )

    # For back compatibility, check if the properties were added already as part of create parent run dto.
    # If not, add it here. Note that this should be removed once JOS changes are stably deployed
    if (
        Properties.DISPLAY_TASK_TYPE_PROPERTY not in experiment_state.current_run.properties or
            Properties.SDK_DEPENDENCIES_PROPERTY not in experiment_state.current_run.properties
    ):
        properties_to_update = get_current_run_properties_to_update(experiment_state)
        experiment_state.current_run.add_properties(properties_to_update)


def take_snapshot(experiment_state):
    """
    Take a snapshot of the user's folder and upload it for remote run consumption. This is necessary if the user
    has any files that need to be included (e.g. the data script).
    """
    snapshot_id = None
    try:
        snapshot_id = cast(AutoMLRun, experiment_state.current_run).take_snapshot(
            experiment_state.automl_settings.path
        )
        logger.info("Snapshot_id: {0}".format(snapshot_id))
        return snapshot_id
    except SnapshotException as se:
        # Snapshot Size was either greater than 300MB or exceeded max files allowed
        if ((str(SNAPSHOT_MAX_SIZE_BYTES / ONE_MB) in se.message) or (str(SNAPSHOT_MAX_FILES) in se.message)):
            logging_utilities.log_traceback(se, logger)
            raise SnapshotException._with_error(
                AzureMLError.create(
                    SnapshotLimitExceeded, target="automl_config.path",
                    size=str(SNAPSHOT_MAX_SIZE_BYTES / ONE_MB), files=str(SNAPSHOT_MAX_FILES)
                )
            )
        else:
            raise
    except (AzureMLException, AzureMLServiceException):
        raise
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        return snapshot_id
