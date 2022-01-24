# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional

from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.dataprep import Dataflow


class LazyTabularData:
    """
    An lazy representation of the Dataset required for machine learning experiments.
    """
    # A reference codes for errors originating from this.
    _REFERENCE_CODE = ReferenceCodes._LAZY_TABULAR_DATA_GENERIC

    def __init__(self, data: Dataflow, label_column_name: str, weight_column_name: Optional[str] = None):
        """
        Initialize the lazy tabular data.

        :param data: dataflow pointing at actual data.
        :param label_column_name: The label column to predict.
        :param weight_column_name: An optional column name representing the weights.
        """
        self.data = data
        self.label_column_name = label_column_name
        self.weight_column_name = weight_column_name

        self._validate()

    def _validate(self) -> None:
        """Does some sanity checks on inputs."""
        Contract.assert_value(self.data, "data", reference_code=LazyTabularData._REFERENCE_CODE)
        Contract.assert_value(self.data, "label_column_name", reference_code=LazyTabularData._REFERENCE_CODE)
