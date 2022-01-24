# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Holding the streaming data context classes."""
import logging
import os
from typing import Any, Optional, List

import azureml.dataprep as dprep
import numpy as np

from azureml.automl.runtime.featurization.streaming import StreamingFeaturizationTransformer
from .data_context import BaseDataContext


class StreamingTransformedDataContext(BaseDataContext):
    """
    The user provided data with applied transformations.

    If there is no preprocessing this will be the same as the RawDataContext.
    This class will also hold the necessary transformers used for Streaming.
    """

    def __init__(self,
                 training_data: dprep.Dataflow,
                 label_column_name: str,
                 raw_data_snapshot: str,
                 output_data_snapshot: str,
                 x_raw_column_names: np.ndarray,
                 weight_column_name: Optional[str] = None,
                 validation_data: Optional[dprep.Dataflow] = None,
                 logger: Any = logging.getLogger(__name__)):
        """
        Construct the StreamingTransformedDataContext class.

        :param training_data: Input training data.
        :type training_data: Dataflow
        :param label_column_name: Target column name.
        :type label_column_name: string
        :param raw_data_snapshot: An example of what the raw data looks like, for inferences
        :type raw_data_snapshot: string
        :param output_data_snapshot: An example of what the output data looks like, for inferences
        :type output_data_snapshot: string
        :param weight_column_name: Weight column name.
        :type weight_column_name: string
        :param validation_data: Validation data.
        :type validation_data: Dataflow
        :param x_raw_column_names: raw feature names of X data.
        :type x_raw_column_names: numpy.ndarray
        :param logger: module logger
        :type logger: logger
        """
        columns_to_drop = []
        sample_weight = None
        y = None

        if label_column_name is not None:
            columns_to_drop.append(label_column_name)
            y = training_data.keep_columns(label_column_name)

        if weight_column_name is not None:
            columns_to_drop.append(weight_column_name)
            sample_weight = training_data.keep_columns(weight_column_name)

        X = training_data.drop_columns(columns_to_drop)

        if validation_data is not None:
            X_valid = validation_data.drop_columns(columns_to_drop)
            y_valid = validation_data.keep_columns(label_column_name) \
                if label_column_name is not None else None
            sample_weight_valid = validation_data.keep_columns(weight_column_name) \
                if weight_column_name is not None else None

        self.raw_data_snapshot = raw_data_snapshot
        self.output_snapshot = output_data_snapshot

        super().__init__(X=X, y=y,
                         X_valid=X_valid,
                         y_valid=y_valid,
                         sample_weight=sample_weight,
                         sample_weight_valid=sample_weight_valid,
                         x_raw_column_names=x_raw_column_names,
                         training_data=training_data,
                         label_column_name=label_column_name,
                         weight_column_name=weight_column_name,
                         validation_data=validation_data)

        self.module_logger = logger
        if self.module_logger is None:
            self.module_logger = logging.getLogger(__name__)
            self.module_logger.propagate = False

        self._featurization_transformer = None  # type: Optional[StreamingFeaturizationTransformer]
        self._featurized_column_names = None  # type: Optional[List[str]]

    def _set_raw_data_snapshot_str(self, data_snapshot_str: str) -> None:
        """Set the data snapshot for the raw data."""
        self.raw_data_snapshot = data_snapshot_str

    def _set_output_snapshot_str(self, output_snapshot_str: str) -> None:
        """Set the data snapshot for the raw data."""
        self.output_snapshot = output_snapshot_str

    def _get_engineered_feature_names(self):
        """Get the engineered feature names available in different transformer."""
        return self.x_raw_column_names

    # todo This class doesn't appear to need this function - deprecate this
    def _clear_cache(self) -> None:
        """Clear the in-memory cached data to lower the memory consumption."""
        # Nothing to clear here
        return

    def _is_cross_validation_scenario(self) -> bool:
        """
        Return 'True' if cross-validation was configured by user.

        Streaming doesnt currently support cv so we always return false.
        """
        return False

    def _get_dataset_categoricals(self, data_type: str) -> List[int]:
        """
        Get the dataset categoricals for given datatype,
        Returns empty list for streaming as this is not supported
        """
        return []

    def set_featurization_transformer(self, featurization_transformer: StreamingFeaturizationTransformer) -> None:
        assert featurization_transformer is not None, "Cannot set featurization_transformer to None"
        self._featurization_transformer = featurization_transformer

    def get_featurization_transformer(self) -> Optional[StreamingFeaturizationTransformer]:
        return self._featurization_transformer

    def get_featurized_column_names(self) -> List[str]:
        # Feature columns would be the same as the raw columns in the training data if there is no featurization
        if self._featurized_column_names:
            return self._featurized_column_names

        raw_columns = self.x_raw_column_names.tolist()  # type: List[str]
        return raw_columns

    def set_featurized_column_names(self, _featurized_column_names: List[str]) -> None:
        self._featurized_column_names = _featurized_column_names
