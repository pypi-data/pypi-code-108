# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import numpy as np
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AllTargetsNan
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.runtime._data_definition import MaterializedTabularData
from azureml.automl.runtime._ml_engine.validation import MaterializedTabularDataValidator
from azureml.automl.runtime.shared import utilities as runtime_utilities


class StreamingTabularDataValidator(MaterializedTabularDataValidator):
    """
    Class to validate a sub-sampled and materialized tabular data in a streaming context.
    """

    def __init__(self, task_type: str, primary_metric: str, is_featurization_required: bool):
        super(StreamingTabularDataValidator, self).__init__(
            task_type=task_type,
            primary_metric=primary_metric,
            is_onnx_enabled=False,  # ONNX unsupported for Streaming
            is_featurization_required=is_featurization_required,
        )

    # override
    def _check_data_can_be_preprocessed(self, tabular_data: MaterializedTabularData) -> None:
        """
        Validate whether `unique` can be calculated on each of the columns within the tabular data.
        Pre-processing data in AutoML requires that pandas.unique can be run safely.

        :param tabular_data: Data to validate.
        :return: None
        """
        # Streaming algorithms (i.e., the ones used via. NimbusML) don't have such stringent requirements
        return

    # override
    def _check_target_column(self, y: np.ndarray) -> None:
        """
        Validate the data in target column (i.e. the column to predict)

        :param y: The input target column to validate
        :return: None
        """
        Contract.assert_value(y, "y")
        # Check if not all values in the target column are Null / NaN
        if len(runtime_utilities._get_indices_missing_labels_output_column(y)) == y.shape[0]:
            raise DataException(azureml_error=AzureMLError.create(AllTargetsNan, target="y"))
