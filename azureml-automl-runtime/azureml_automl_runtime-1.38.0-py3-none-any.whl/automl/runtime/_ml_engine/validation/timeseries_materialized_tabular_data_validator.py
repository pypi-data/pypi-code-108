# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import numpy as np

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TimeseriesDfWrongTypeOfValueColumn
from azureml.automl.core.shared.constants import Tasks
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from .materialized_tabular_data_validator import MaterializedTabularDataValidator


class TimeseriesMaterializedTabularDataValidator(MaterializedTabularDataValidator):
    """
    Validator for validating the materialized tabular data for a timeseries task.
    """

    def __init__(self, primary_metric: str) -> None:
        """
        Construct a TimeseriesMaterializedTabularDataValidator to validate the tabular data.
        :param primary_metric: The metric to optimize for.
        """
        super(TimeseriesMaterializedTabularDataValidator, self).__init__(
            task_type=Tasks.FORECASTING,
            primary_metric=primary_metric,
            is_onnx_enabled=False,
            is_featurization_required=True,
        )

    # override
    def _check_target_column(self, y: np.ndarray) -> None:
        """
        Validate the time / grain column.

        :param y: The input target column to validate
        :return: None
        :raises: ForecastingDataException if y contains non numeric values.
        """
        # TODO: Move timeseries specific time/grain column validations here
        if len(y.shape) == 2 and y.shape[1] == 1:
            y = y.flatten()
        if not all(isinstance(v, (int, float, np.number)) for v in y):
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    TimeseriesDfWrongTypeOfValueColumn,
                    target='target_column',
                    reference_code=ReferenceCodes._TSDF_WRONG_TYPE_OF_TGT_COL)
            )
