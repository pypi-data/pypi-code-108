# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Auto ML common logging module."""
import logging
from typing import Any, Dict, Optional

from azureml.telemetry.contracts import (RequiredFieldKeys,
                                         StandardFieldKeys,
                                         ExtensionFieldKeys)

from azureml.automl.core._logging import log_server
from azureml.automl.core.shared import logging_fields
from ._azureautomlsettings import AzureAutoMLSettings
from .constants import ComputeTargets
from .utilities import _InternalComputeTypes

logger = logging.getLogger(__name__)

UNKNOWN_VALUE = "UNKNOWN"


def set_run_custom_dimensions(
        automl_settings: Optional[AzureAutoMLSettings],
        parent_run_id: Optional[str],
        child_run_id: Optional[str] = None,
        run_id: Optional[str] = None,
        parent_run_uuid: Optional[str] = None,
        child_run_uuid: Optional[str] = None,
        code_path: str = UNKNOWN_VALUE) -> None:
    """
    Create the logger with telemetry hook.

    :param automl_settings: the AutoML settings object
    :param parent_run_id: parent run id
    :param child_run_id: child run id
    :param run_id: run id for any other AutoML scenario like Model Explanation or Test Run
    :param parent_run_uuid: Parent run UUID
    :param child_run_uuid: Child run UUID
    :param code_path: What type of execution is happening. e.g. remote, local, local-managed, adb.
    :return
    """
    # Get version numbers for the modules (these are best effort, shouldn't be fatal for the run)
    automl_train_sdk_version = get_automl_train_sdk_version()
    automl_core_sdk_version = get_automl_core_sdk_version()

    custom_dimensions = {
        "automl_client": "azureml",
        "automl_sdk_version": automl_train_sdk_version,
        "automl_core_sdk_version": automl_core_sdk_version,
        "code_path": code_path
    }  # type: Dict[str, Optional[Any]]

    fields = {
        RequiredFieldKeys.CLIENT_TYPE_KEY: 'sdk',
        RequiredFieldKeys.CLIENT_VERSION_KEY: automl_train_sdk_version,
        RequiredFieldKeys.COMPONENT_NAME_KEY: logging_fields.TELEMETRY_AUTOML_COMPONENT_KEY,
        logging_fields.AutoMLExtensionFieldKeys.AUTOML_SDK_VERSION_KEY: automl_train_sdk_version,
        logging_fields.AutoMLExtensionFieldKeys.AUTOML_CORE_SDK_VERSION_KEY: automl_core_sdk_version,
        ExtensionFieldKeys.DISK_USED_KEY: None
    }

    task_type = UNKNOWN_VALUE  # type: Optional[str]
    compute_target = UNKNOWN_VALUE  # type: Optional[str]
    subscription_id = UNKNOWN_VALUE  # type: Optional[str]
    region = UNKNOWN_VALUE  # type: Optional[str]
    if automl_settings is not None:
        if automl_settings.is_timeseries:
            task_type = "forecasting"
        else:
            task_type = automl_settings.task_type

        # Override compute target based on environment.
        compute_target = _InternalComputeTypes.identify_compute_type(compute_target=automl_settings.compute_target,
                                                                     azure_service=automl_settings.azure_service)
        if not compute_target:
            if automl_settings.compute_target == ComputeTargets.LOCAL:
                compute_target = _InternalComputeTypes.LOCAL
            elif automl_settings.compute_target == ComputeTargets.AMLCOMPUTE:
                compute_target = _InternalComputeTypes.AML_COMPUTE
            elif automl_settings.spark_service == 'adb':
                compute_target = _InternalComputeTypes.DATABRICKS
            else:
                compute_target = _InternalComputeTypes.REMOTE

        subscription_id = automl_settings.subscription_id

        region = automl_settings.region

    custom_dimensions.update(
        {
            "task_type": task_type,
            "compute_target": compute_target,
            "subscription_id": subscription_id,
            "region": region
        }
    )

    fields[StandardFieldKeys.ALGORITHM_TYPE_KEY] = task_type
    # Don't fill in the Compute Type as it is being overridden downstream by Execution service
    # ComputeTarget field is still logged in customDimensions that contains these values
    # fields[StandardFieldKeys.COMPUTE_TYPE_KEY] = compute_target

    fields[RequiredFieldKeys.SUBSCRIPTION_ID_KEY] = subscription_id
    # Workspace name can have PII information. Therefore, not including it.
    # fields[RequiredFieldKeys.WORKSPACE_ID_KEY] = automl_settings.workspace_name

    snake_cased_fields = {
        logging_fields.camel_to_snake_case(field_name): field_value
        for field_name, field_value in fields.items()
    }

    if parent_run_id is not None:
        log_server.update_custom_dimension(parent_run_id=parent_run_id)

    if run_id is not None:
        log_server.update_custom_dimension(run_id=run_id)
    if child_run_id is not None:
        log_server.update_custom_dimension(run_id=child_run_id)
    elif parent_run_id is not None:
        log_server.update_custom_dimension(run_id=parent_run_id)

    if parent_run_uuid is not None:
        log_server.update_custom_dimension(parent_run_uuid=parent_run_uuid)

    if child_run_uuid is not None:
        log_server.update_custom_dimension(run_uuid=child_run_uuid)

    log_server.update_custom_dimensions(custom_dimensions)
    log_server.update_custom_dimensions(snake_cased_fields)


def get_automl_core_sdk_version() -> str:
    automl_core_sdk_version = UNKNOWN_VALUE
    try:
        import azureml.automl.core
        automl_core_sdk_version = azureml.automl.core.VERSION
    except Exception as e:
        logger.warning("Failed to get version information for the module 'azureml.automl.core'. "
                       "Exception Type: {}".format(type(e)))
    return automl_core_sdk_version


def get_automl_train_sdk_version() -> str:
    azure_automl_sdk_version = UNKNOWN_VALUE
    try:
        import azureml.train.automl
        azure_automl_sdk_version = azureml.train.automl.VERSION
    except Exception as e:
        logger.warning("Failed to get version information for the module 'azureml.train.automl'. "
                       "Exception Type: {}".format(type(e)))
    return azure_automl_sdk_version
