# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for interacting with azureml.dataprep."""
import json
import logging
from typing import Any, Dict, NoReturn, Optional

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (ContentModified,
                                                                              DatabaseQuery,
                                                                              DataPathInaccessible,
                                                                              DataPathNotFound,
                                                                              DataprepScriptExecution,
                                                                              DataprepStepTranslation,
                                                                              DataprepValidation,
                                                                              DatasetFileRead,
                                                                              DatastoreNotFound,
                                                                              InsufficientMemory,
                                                                              MissingSecrets)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import DataprepException
from azureml.automl.core.shared.exceptions import (ClientException,
                                                   ConfigException,
                                                   ResourceException)
from azureml.dataprep import DataPrepException as DprepException


DATAPREP_INSTALLED = True
try:
    import azureml.dataprep as dprep
except ImportError:
    DATAPREP_INSTALLED = False
try:
    from dprep.api.dataflow import Dataflow
except ImportError:
    Dataflow = Any


__activities_flag__ = 'activities'


logger = logging.getLogger(__name__)

# DPrep exceptions currently can't be converted to ErrorResponses, hence the mapping below.
DATAPREP_ERROR_MAP = {
    "Validation": DataprepValidation,
    "StreamAccess.NotFound": DataPathNotFound,
    "StreamAccess.Authentication": DataPathInaccessible,
    # We've timed out on reading the data from the storage account.
    "StreamAccess.TimeoutExpired": DatasetFileRead,
    "StreamAccess.ContentModified": ContentModified,
    "ScriptExecution.StreamAccess": DataprepScriptExecution,
    "DatastoreResolution.NotFound": DatastoreNotFound,
    "ScriptExecution.DatastoreResolution": DataprepScriptExecution,
    "ScriptExecution.Transformation": DataprepScriptExecution,
    "ScriptExecution.ReadDataFrame": DataprepScriptExecution,
    "ScriptExecution.DatabaseQuery": DatabaseQuery,
    "ScriptExecution.Database": DataprepScriptExecution,
    "StepTranslation": DataprepStepTranslation,
    # This shouldn't happen once we've migrated completely to rely on TabularDatasets, since the credentials are
    # handled automatically by the Dataset infra.
    "MissingSecrets": MissingSecrets,
}


def get_dataprep_json(X: Optional[Dataflow] = None,
                      y: Optional[Dataflow] = None,
                      sample_weight: Optional[Dataflow] = None,
                      X_valid: Optional[Dataflow] = None,
                      y_valid: Optional[Dataflow] = None,
                      sample_weight_valid: Optional[Dataflow] = None,
                      cv_splits_indices: Optional[Dataflow] = None) -> Optional[str]:
    """
    Get dataprep json.

    :param X: Training features.
    :type X: azureml.dataprep.Dataflow
    :param y: Training labels.
    :type y: azureml.dataprep.Dataflow
    :param sample_weight: Sample weights for training data.
    :type sample_weight: azureml.dataprep.Dataflow
    :param X_valid: validation features.
    :type X_valid: azureml.dataprep.Dataflow
    :param y_valid: validation labels.
    :type y_valid: azureml.dataprep.Dataflow
    :param sample_weight_valid: validation set sample weights.
    :type sample_weight_valid: azureml.dataprep.Dataflow
    :param cv_splits_indices: custom validation splits indices.
    :type cv_splits_indices: azureml.dataprep.Dataflow
    :return: JSON string representation of a dict of Dataflows
    """
    dataprep_json = None
    df_value_list = [X, y, sample_weight, X_valid,
                     y_valid, sample_weight_valid, cv_splits_indices]
    if any(var is not None for var in df_value_list):
        dataflow_dict = {
            'X': X,
            'y': y,
            'sample_weight': sample_weight,
            'X_valid': X_valid,
            'y_valid': y_valid,
            'sample_weight_valid': sample_weight_valid
        }
        if cv_splits_indices is not None:
            # Note that there is currently no scenario where we accept cv_splits_indices as Dataflow arrays.
            # We validate upfront that these are passed as numpy arrays, and are passed as cv_split_columns in case
            # of remote / adb runs.
            # The below code is there just for completeness, and the method can be refactored to not accept
            # cv_splits_indices at all.
            for i in range(len(cv_splits_indices or [])):
                split = cv_splits_indices[i]
                if not is_dataflow(split):
                    logger.warning("cannot serialize 'cv_splits_indices' of type {}".format(type(split)))
                else:
                    dataflow_dict['cv_splits_indices_{0}'.format(i)] = split
        dataprep_json = save_dataflows_to_json(dataflow_dict)
        Contract.assert_value(dataprep_json, "dataprep_json")

    return dataprep_json


def get_dataprep_json_dataset(training_data: Optional[Dataflow] = None,
                              validation_data: Optional[Dataflow] = None,
                              test_data: Optional[Dataflow] = None) -> Optional[str]:
    """
    Get dataprep json.

    :param training_data: Training data.
    :type training_data: azureml.dataprep.Dataflow
    :param validation_data: Validation data
    :type validation_data: azureml.dataprep.Dataflow
    :param test_data: Test data
    :type test_data: azureml.dataprep.Dataflow
    :return: JSON string representation of a dict of Dataflows
    """
    dataprep_json = None
    df_value_list = [training_data, validation_data, test_data]
    if any(var is not None for var in df_value_list):
        dataflow_dict = {
            'training_data': training_data,
            'validation_data': validation_data,
            'test_data': test_data
        }
        dataprep_json = save_dataflows_to_json(dataflow_dict)
        Contract.assert_value(dataprep_json, "dataprep_json")

    return dataprep_json


def save_dataflows_to_json(dataflow_dict: Dict[str, Dataflow]) -> Optional[str]:
    """
    Save dataflows to json.

    :param dataflow_dict: the dict with key as dataflow name and value as dataflow
    :type dataflow_dict: dict(str, azureml.dataprep.Dataflow)
    :return: the JSON string representation of a dict of Dataflows
    """
    dataflow_json_dict = {}     # type: Dict[str, Any]
    for name in dataflow_dict:
        dataflow = dataflow_dict[name]
        if not is_dataflow(dataflow):
            continue
        try:
            # json.dumps(json.loads(...)) to remove newlines and indents
            dataflow_json = json.dumps(json.loads(dataflow.to_json()))
        except DprepException as e:
            dataprep_error_handler(e)
        except Exception as e:
            # at this point we don't know what went wrong, so raising a system error
            raise DataprepException.from_exception(e).with_generic_msg('Error when saving dataflows to JSON.')
        dataflow_json_dict[name] = dataflow_json

    if len(dataflow_json_dict) == 0:
        return None

    dataflow_json_dict[__activities_flag__] = 0  # backward compatible with old Jasmine
    return json.dumps(dataflow_json_dict)


def load_dataflows_from_json_dict(dataflow_json_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load dataflows from json dict.

    :param dataprep_json: the JSON string representation of a dict of Dataflows
    :type dataprep_json: str
    :return: a dict with key as dataflow name and value as dataflow, or None if JSON is malformed
    """
    if __activities_flag__ in dataflow_json_dict:
        del dataflow_json_dict[__activities_flag__]  # backward compatible with old Jasmine

    dataflow_dict = {}
    for name in dataflow_json_dict:
        try:
            dataflow = dprep.Dataflow.from_json(dataflow_json_dict[name])
        except DprepException as e:
            dataprep_error_handler(e)
        except Exception as e:
            # at this point we don't know what went wrong, so raising a system error
            raise DataprepException.from_exception(e)
        dataflow_dict[name] = dataflow
    return dataflow_dict


def is_dataflow(dataflow: Dataflow) -> bool:
    """
    Check if object passed is of type dataflow.

    :param dataflow: The value to be checked.
    :return: True if dataflow is of type azureml.dataprep.Dataflow
    """
    if not DATAPREP_INSTALLED or not isinstance(dataflow, dprep.Dataflow):
        return False
    return True


def dataprep_error_handler(e: DprepException) -> NoReturn:
    """Handle dataprep errors.

    param e: The exception raised by dataprep service
    type: DprepException
    """
    generic_msg = 'Failed to get data from DataPrep. ErrorCode: {0}. Message: {1}'.format(
        e.error_code, getattr(e, 'compliant_message', ''))
    logger.error(generic_msg)
    if "OutOfMemory" in e.error_code:
        raise ResourceException._with_error(AzureMLError.create(InsufficientMemory,), inner_exception=e) from e
    for error_substring in DATAPREP_ERROR_MAP:
        if error_substring in e.error_code:
            error = AzureMLError.create(DATAPREP_ERROR_MAP[error_substring], dprep_error=str(e))
            raise ConfigException(azureml_error=error, inner_exception=e)
    raise ClientException.from_exception(e).with_generic_msg(generic_msg)
