# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, List, Optional, cast

import numpy as np
import pandas as pd

from azureml.data import TabularDataset
from azureml.automl.runtime.shared.types import DataInputType
from scipy import sparse

from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.runtime._data_definition.raw_experiment_data import RawExperimentData
from azureml.automl.runtime.faults_verifier import VerifierManager
from azureml.automl.runtime._ml_engine.validation import common_data_validations
from azureml.automl.runtime import dataprep_utilities, training_utilities
from azureml.automl.runtime import _data_splitting_utilities, _data_transformation_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings


def _get_raw_experiment_data_from_data_script(
        get_data_script: Any, automl_settings: AutoMLBaseSettings
) -> RawExperimentData:
    """
    Parse the user provided get_data script and return a RawExperimentData out of it.

    This is a deprecated functionality.

    :param get_data_script:
    :param automl_settings:
    :return:
    """
    Contract.assert_value(get_data_script, "get_data_script")

    data_dict = training_utilities._extract_user_data(get_data_script)
    X = data_dict.get('X')
    y = data_dict.get('y')
    sample_weight = data_dict.get('sample_weight')
    X_valid = data_dict.get('X_valid')
    y_valid = data_dict.get('y_valid')
    sample_weight_valid = data_dict.get('sample_weight_valid')
    cv_splits_indices = data_dict.get("cv_splits_indices")
    feature_column_names = data_dict.get("x_raw_column_names")

    return _get_raw_experiment_data_legacy(
        automl_settings, X, y, sample_weight, X_valid, y_valid, sample_weight_valid,
        cv_splits_indices, feature_column_names
    )


def _get_raw_experiment_data_from_pandas_dataframe(
        training_data: pd.DataFrame,
        automl_settings: AutoMLBaseSettings,
        validation_data: Optional[pd.DataFrame] = None
) -> RawExperimentData:
    Contract.assert_type(training_data, "training_data", expected_types=pd.DataFrame)
    Contract.assert_type(automl_settings, "automl_settings", expected_types=AutoMLBaseSettings)
    label_column_name = cast(str, automl_settings.label_column_name)

    cv_splits_indices = None
    X, y, weights, cv_splits_indices = training_utilities._extract_data_from_combined_dataframe(
        training_data=training_data, label_column_name=label_column_name,
        sample_weight_column_name=automl_settings.weight_column_name,
        cv_split_column_names=automl_settings.cv_split_column_names
    )

    X_valid = None  # type: Optional[pd.DataFrame]
    y_valid = None  # type: Optional[np.ndarray]
    weights_valid = None    # type: Optional[np.ndarray]
    if validation_data is not None:
        Contract.assert_type(training_data, "validation_data", expected_types=pd.DataFrame)
        X_valid, y_valid, weights_valid, _ = training_utilities._extract_data_from_combined_dataframe(
            training_data=validation_data, label_column_name=label_column_name,
            sample_weight_column_name=automl_settings.weight_column_name
        )

    return RawExperimentData(
        X=X,
        y=y,
        weights=weights,
        X_valid=X_valid,
        y_valid=y_valid,
        weights_valid=weights_valid,
        target_column_name=automl_settings.label_column_name,
        feature_column_names=X.columns.values,
        weight_column_name=automl_settings.weight_column_name,
        validation_size=automl_settings.validation_size,
        cv_splits_indices=cv_splits_indices,
        n_cross_validations=automl_settings.n_cross_validations,
    )


def _get_raw_experiment_data_from_datasets(
        training_data: TabularDataset,
        automl_settings: AutoMLBaseSettings,
        validation_data: Optional[TabularDataset] = None
) -> RawExperimentData:
    """
    Given training / validation datasets in AzureML's TabularDataset format, materialize it as a pandas DataFrame,
    dividing the datastets into raw features ('X') + target column ('y').
    If weights and cv splits columns were specified, those are also materialized and returned as numpy arrays.
    All data objects are wrapped within a RawExperimentData.

    :param training_data:
    :param automl_settings:
    :param validation_data:
    :return:
    """
    Contract.assert_type(training_data, "training_data", expected_types=TabularDataset)

    training_dataflow = training_data._dataflow
    validation_dataflow = validation_data._dataflow if validation_data is not None else None

    training_data_pd = dataprep_utilities.materialize_dataflow(training_dataflow)

    validation_data_pd = None   # type: Optional[pd.DataFrame]
    if validation_data is not None:
        Contract.assert_type(validation_data, "validation_data", expected_types=TabularDataset)
        validation_data_pd = dataprep_utilities.materialize_dataflow(validation_dataflow)

    return _get_raw_experiment_data_from_pandas_dataframe(
        training_data_pd, automl_settings, validation_data_pd
    )


def _get_raw_experiment_data_from_training_data(
        training_data: DataInputType,
        automl_settings: AutoMLBaseSettings,
        validation_data: Optional[DataInputType]
) -> RawExperimentData:
    if isinstance(training_data, pd.DataFrame):
        if validation_data is not None:
            Validation.validate_type(validation_data, "validation_data", expected_types=pd.DataFrame)
        return _get_raw_experiment_data_from_pandas_dataframe(training_data, automl_settings, validation_data)
    elif isinstance(training_data, TabularDataset):
        if validation_data is not None:
            Validation.validate_type(validation_data, "validation_data", expected_types=TabularDataset)
        return _get_raw_experiment_data_from_datasets(training_data, automl_settings, validation_data)
    else:
        raise NotImplementedError("Unrecognized data format")


def _get_raw_experiment_data_legacy(
        automl_settings: AutoMLBaseSettings,
        X: Optional[Any],
        y: Optional[Any],
        weights: Optional[Any] = None,
        X_valid: Optional[Any] = None,
        y_valid: Optional[Any] = None,
        weights_valid: Optional[Any] = None,
        cv_splits_indices: Optional[Any] = None,
        x_raw_column_names: Optional[Any] = None
) -> RawExperimentData:
    """
    To be called when inputs are specified in the old style as X, y, X_valid, y_valid etc.
    """
    Contract.assert_value(automl_settings, "automl_settings")
    Contract.assert_value(X, "X")
    Contract.assert_value(y, "y")

    X = dataprep_utilities.materialize_dataflow(X)
    if X_valid is not None:
        X_valid = dataprep_utilities.materialize_dataflow(X_valid)

    y = dataprep_utilities.materialize_dataflow(y, as_numpy=True)
    if y_valid is not None:
        y_valid = dataprep_utilities.materialize_dataflow(y_valid, as_numpy=True)

    if weights is not None:
        weights = dataprep_utilities.materialize_dataflow(weights, as_numpy=True)
    if weights_valid is not None:
        weights_valid = dataprep_utilities.materialize_dataflow(weights_valid, as_numpy=True)

    if isinstance(X, pd.DataFrame):
        # reset index in case a customer's df contains index column(s)
        X.reset_index(inplace=True, drop=True)
        # Cache the raw column names if available
        x_raw_column_names = X.columns.values

        # reset index in case a customer's df contains index column(s)
        if X_valid is not None:
            X_valid.reset_index(inplace=True, drop=True)
    elif isinstance(X, np.ndarray) or sparse.issparse(X):
        X = _data_transformation_utilities._add_raw_column_names_to_X(X)
        if X_valid is not None:
            X_valid = _data_transformation_utilities._add_raw_column_names_to_X(X_valid)

    y = cast(np.ndarray, training_utilities._convert_to_numpy_maybe(y, 'y'))
    y_valid = cast(np.ndarray, training_utilities._convert_to_numpy_maybe(y_valid, 'y_valid'))

    if cv_splits_indices is not None:
        cv_splits_indices = dataprep_utilities.resolve_cv_splits_indices(cv_splits_indices)

    if isinstance(weights, pd.DataFrame):
        weights = weights.values
    if isinstance(weights_valid, pd.DataFrame):
        weights_valid = weights_valid.values

    return RawExperimentData(
        X=X,
        y=y,
        weights=weights,
        X_valid=X_valid,
        y_valid=y_valid,
        weights_valid=weights_valid,
        target_column_name=automl_settings.label_column_name,
        feature_column_names=x_raw_column_names,
        weight_column_name=automl_settings.weight_column_name,
        validation_size=automl_settings.validation_size,
        cv_splits_indices=cv_splits_indices,
        n_cross_validations=automl_settings.n_cross_validations,
    )


def preprocess_experiment_data(
        raw_experiment_data: RawExperimentData,
        automl_settings: AutoMLBaseSettings,
        verifier: VerifierManager
) -> RawExperimentData:
    """
    TO be called only for C + R

    # This does all rule based splitting, for train, valid, test.
    # Should eventually evolve into one stop place for cleaning NaNs, dropping rows etc.

    :param train_data:
    :param automl_settings:
    :param verifier:
    :return:
    """
    common_data_validations.check_dimensions(
        X=raw_experiment_data.X,
        y=raw_experiment_data.y,
        X_valid=raw_experiment_data.X_valid,
        y_valid=raw_experiment_data.y_valid,
        sample_weight=raw_experiment_data.weights,
        sample_weight_valid=raw_experiment_data.weights_valid
    )

    try:
        # Update the original training data / settings, if test or validation size was provided, or we needed to
        # apply a manual validation strategy
        _data_splitting_utilities.update_training_data_splits(raw_experiment_data, automl_settings, verifier)
    except Exception as e:
        # At this point, user datasets are not validated. Hence, known errors during splitting should be raised with
        # user error codes.
        common_data_validations.materialized_tabular_data_user_error_handler(e)

    return raw_experiment_data
