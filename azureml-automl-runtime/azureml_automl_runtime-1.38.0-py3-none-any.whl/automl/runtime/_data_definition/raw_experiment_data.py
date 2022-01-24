# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, cast, Dict, List, Optional

import numpy as np
import pandas as pd

from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from .types import DataFrameLike


class RawExperimentData:
    """
    A data structure that combines all the pieces of a Dataset required to perform a Machine Learning experiment, such
    as training data (on which the model trains on), validation data (on which we evaluate the model predictability),
    weights data) that each sample from the training data is to be assigned) etc.

    All different possibilities of inputs converge to this class, which presents a unified interface for the
    underlying clients to use, which means that the clients of this class should not care which way the inputs
    were provided to it (e.g. get data script, X + y + w, training_data, validation_data, etc.)

    Note that this class is only the convergence point of all different formats that we support in AutoML. It does not
    ensure that the underlying data is valid, i.e. it is a pre-validation concept.
    """

    def __init__(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        weights: Optional[np.ndarray] = None,
        X_valid: Optional[pd.DataFrame] = None,
        y_valid: Optional[np.ndarray] = None,
        weights_valid: Optional[np.ndarray] = None,
        training_data: Optional[DataFrameLike] = None,
        validation_data: Optional[DataFrameLike] = None,
        target_column_name: Optional[str] = None,
        feature_column_names: Optional[np.ndarray] = None,
        weight_column_name: Optional[str] = None,
        validation_size: Optional[float] = 0,
        cv_splits_indices: Optional[List[List[Any]]] = None,
        n_cross_validations: Optional[int] = None,
        X_test: Optional[pd.DataFrame] = None,
        y_test: Optional[np.ndarray] = None,
        data_snapshot_str: str = ""
    ):
        """
        Initialize a RawExperimentData.

        :param X: The features (or columns) to train the model on.
        :param y: The target column (e.g., labels) to predict.
        :param weights: An optional column representing the weight to be assigned to each sample in X.
        :param X_valid: A validation dataset with the same schema as X.
        :param y_valid: The target column for the data in X_valid.
        :param weights_valid: Weights for the samples in X_valid.
        :param training_data: Optional reference to the complete underlying training dataset on the backing store.
        :param validation_data: An optional validation dataset with the same schema as training_data.
        :param target_column_name: Name of the column to predict. Note that this can be empty when X is a numpy array.
        :param feature_column_names: The names of columns in X or training_data on which to train the model on.
        :param weight_column_name: Column name representing the weights to be assigned to each sample in train data.
        :param validation_size: Fraction of the data to hold out as validation data during model selection.
        :param cv_splits_indices: Optional list of indices in X to use for various cross folds during model selection.
        :param n_cross_validations: The number of cross validations to perform.
        :param X_test: Data to test the model on.
        :param y_test: Targets for the test data.
        :param data_snapshot_str: The input data snapshot string.
        """
        # data
        self.X, self.y, self.weights = X, y, weights
        self.X_valid, self.y_valid, self.weights_valid = X_valid, y_valid, weights_valid
        self.training_data, self.validation_data = training_data, validation_data
        self.X_test, self.y_test = X_test, y_test

        # metadata & configuration
        self.target_column_name = target_column_name
        self.feature_column_names = feature_column_names
        self.weight_column_name = weight_column_name
        self.validation_size = validation_size
        self.cv_splits_indices = cv_splits_indices
        self.n_cross_validations = n_cross_validations
        self.data_snapshot_str = data_snapshot_str

    @classmethod
    def create(cls,
               data_dictionary: Dict[str, Any],
               label_column_name: Optional[str],
               weight_column_name: Optional[str],
               validation_size: Optional[float],
               n_cross_validations: Optional[int]) -> "RawExperimentData":
        """
        Initialize a RawExperimentData using a data dictionary containing dataset related parameters, and an
        AutoML settings object.
        The keys expected within the dictionary are:
            - X, y, sample_weights, X_valid, y_valid, sample_weights_valid, cv_splits_indices (For legacy data inputs)
            - training_data, validation_data (For new style data inputs)
            - X_test, y_test (For test data)
            - x_raw_column_names (Legacy behavior, if the inputs are provided as Numpy, a second array for
                feature names is provided)

        :param data_dictionary: A dictionary that contains data params
        :param label_column_name: The name of the label column
        :param weight_column_name: The name of the weight column
        :param validation_size: The size of the validation data relative to the overall data
        :param n_cross_validations: The number of cross validations to use
        :return: An instance of RawExperimentData
        """
        return RawExperimentData(
            X=cast(pd.DataFrame, data_dictionary.get("X")),
            y=cast(np.ndarray, data_dictionary.get("y")),
            weights=data_dictionary.get("sample_weights"),
            X_valid=data_dictionary.get("X_valid"),
            y_valid=data_dictionary.get("y_valid"),
            weights_valid=data_dictionary.get("sample_weights_valid"),
            training_data=data_dictionary.get("training_data"),
            validation_data=data_dictionary.get("validation_data"),
            target_column_name=label_column_name,
            feature_column_names=data_dictionary.get("x_raw_column_names"),
            weight_column_name=weight_column_name,
            validation_size=validation_size,
            cv_splits_indices=data_dictionary.get("cv_splits_indices"),
            n_cross_validations=n_cross_validations,
            X_test=data_dictionary.get("X_test"),
            y_test=data_dictionary.get("y_test"),
        )
