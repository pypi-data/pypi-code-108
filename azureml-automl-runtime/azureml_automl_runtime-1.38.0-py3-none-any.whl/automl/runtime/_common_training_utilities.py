# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The set of helper functions training utilities."""
import logging

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AllTargetsOverlapping, AllTargetsUnique)
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared.utilities import _get_num_unique
from azureml.automl.runtime.shared.types import DataSingleColumnInputType

logger = logging.getLogger(__name__)


def check_target_uniqueness(
        y: DataSingleColumnInputType,
        task_type: str) -> None:
    """
    Check the number of unique values in a column.

    :param y: The input column.
    :param task_type: The AutoML task type.
    """
    y_ravel = y.ravel()
    num_unique_classes = _get_num_unique(y_ravel, ignore_na=True)
    logger.info("{} unique classes detected.".format(num_unique_classes))
    check_all_unique = task_type == constants.Tasks.CLASSIFICATION
    if num_unique_classes < 2 and task_type != constants.Tasks.FORECASTING:
        raise DataException._with_error(
            AzureMLError.create(
                AllTargetsOverlapping, target=task_type, task_type=task_type,
                reference_code=ReferenceCodes._VALIDATE_TARGET_COLUMN_NOT_SINGLE_VALUE
            )
        )

    if check_all_unique and num_unique_classes == y_ravel.shape[0]:
        raise DataException._with_error(
            AzureMLError.create(
                AllTargetsUnique, target=task_type, task_type=task_type,
                reference_code=ReferenceCodes._VALIDATE_TARGET_COLUMN_NOT_ALL_UNIQUE
            )
        )
