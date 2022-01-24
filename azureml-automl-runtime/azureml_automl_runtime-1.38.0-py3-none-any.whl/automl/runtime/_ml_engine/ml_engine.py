# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Principles of MLEngine
1) Composable set of APIs that define the various stages of a machine learning experiment
2) APIs are azure service and azureML SDK independent - (except for AzureML dataset package)
3) APIs are ML package concept independent - ie they should NOT project the concepts from ML packages directly
4) APIs are distributed infra independent - APIs hide distributed-infra used however are take "distributed/not" flag
5) APIs are AutoML concept and automl workflow independent - ie they need to work beyond AutoML context
6) APIs params are explicit - ie they explicitly accept params it expects and wont depend on external state, storage
7) APIs are friendly to AML pipelining - ie we expect these APIs to be orchestratable using AML pipelines

Terminology
1) Pipeline: Assembled set of featurizer(s) and trainer. It is a pre training concept.
2) Model: The thing that comes out of fitting/training. It is a post training concept.
        FeaturizedModel: The thing that comes out fitting a featurizers. Can transform but cant predict.
        ClassificationModel/RegressionModel/ForecastingModel: Can transform(optionally) and predict/forecast.
3) Algorithm: Captures the logic used to train - such as LightGBM or LinearRegressor


Pending APIs
1) prepare
2) detect column_purpose
3) featurizer_fit
4) featurizer_transform
5) predict
6) predict_proba
7) ensemble
8) explain
9) convert_to_onnx
10) forecast
11) evaluate_forecaster
12) evaluate_regressor

"""

import logging
from typing import Dict, Optional, Any, Union, List, Tuple

import numpy as np
import pandas as pd
from scipy import sparse
from skl2onnx.proto import onnx_proto  # noqa: E402
from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline

from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared import constants
from azureml.automl.runtime._data_definition import RawExperimentData, MaterializedTabularData
from azureml.automl.runtime._ml_engine.ensemble import EnsembleSelector
from azureml.automl.runtime._ml_engine.validation import AbstractRawExperimentDataValidator, \
    RawExperimentDataValidator, RawExperimentDataValidatorSettings
from azureml.automl.runtime._ml_engine.validation.streaming_experiment_data_validator import \
    StreamingExperimentDataValidator
from azureml.automl.runtime._runtime_params import ExperimentDataSettings
from azureml.automl.runtime.featurization import AutoMLTransformer
from azureml.automl.runtime.onnx_convert import OnnxConverter
from azureml.automl.runtime.shared.types import DataInputType


def validate(raw_experiment_data: RawExperimentData, validation_settings: RawExperimentDataValidatorSettings,
             data_settings: ExperimentDataSettings) -> None:
    """
    Checks whether data is ready for a Classification / Regression machine learning task

    :param raw_experiment_data: Object which provides access to the training (and/or validation) dataset(s).
    :param automl_settings: The settings for the experiment.
    :return: None
    """
    # TODO: Switch the validator based on the type of input data, rather than automl settings
    experiment_data_validator = None    # type: Optional[AbstractRawExperimentDataValidator]
    if validation_settings.control_settings.enable_streaming:
        experiment_data_validator = StreamingExperimentDataValidator(validation_settings, data_settings)
    else:
        experiment_data_validator = RawExperimentDataValidator(validation_settings)

    experiment_data_validator.validate(raw_experiment_data)


def featurize(
        x: DataInputType, y: DataInputType, transformer: AutoMLTransformer
) -> Union[pd.DataFrame, np.ndarray, sparse.spmatrix]:
    """
    Featurize the data so it could be used for final model training

    :param x: The data to transform.
    :param y: The target column to predict.
    :param transformer: The transformer to use to featurize the dataset
    :return:
    """
    return transformer.fit_transform(x, y)


def convert_to_onnx(
    trained_model: Pipeline,
    metadata_dict: Optional[Dict[str, Any]],
    enable_split_onnx_models: bool = False,
    model_name: str = '',
    model_desc: Optional[Dict[Any, Any]] = None,
) -> Tuple[Optional[onnx_proto.ModelProto],
           Optional[onnx_proto.ModelProto],
           Optional[onnx_proto.ModelProto],
           Dict[Any, Any],
           Optional[Dict[str, Any]]]:
    """
    Convert a regular model to an ONNX model

    :param trained_model: A trained model returned by the "train" method.
    :param metadata_dict: Metadata of the training data returned by the "get_onnx_metadata" method.
    :param enable_split_onnx_models: Enables returns of separate model for the featurizer and estimator.
    :param model_name: The ONNX model name.
    :param model_desc: The ONNX model description.

    :return: A tuple containing:
                 The ONNX model for the whole pipeline
                 Optionally the ONNX model for the featurizer.
                 Optionally the ONNX model for the estimator
    """
    onnx_cvt = OnnxConverter(is_onnx_compatible=True,
                             enable_split_onnx_featurizer_estimator_models=enable_split_onnx_models)

    onnx_cvt.initialize_with_metadata(metadata_dict=metadata_dict)

    onnx_model, featurizer_onnx_model, estimator_onnx_model, err = \
        onnx_cvt.convert(trained_model, model_name, model_desc)

    model_resource = onnx_cvt.get_converted_onnx_model_resource()

    return onnx_model, featurizer_onnx_model, estimator_onnx_model, model_resource, err


def run_ensemble_selection(
        task_type: str,
        training_type: constants.TrainingType,
        fitted_models: List[Union[Pipeline, List[Pipeline]]],
        validation_data: List[MaterializedTabularData],
        metric_to_optimize: str,
        class_labels: Optional[np.ndarray] = None,
        y_transformer: Optional[TransformerMixin] = None,
        y_min: Optional[float] = None,
        y_max: Optional[float] = None,
        selection_iterations: int = 10) -> EnsembleSelector:
    """
    Selects which models produce better scores when used within an Ensemble.
    Returns the indices of the models chosen, along with their weights

    :param task_type: The ML task type (eg. 'classification' or 'regression')
    :param training_type: The way validation is being done (eg. Train & Validate vs Cross Validate)
    :param fitted_models: List of models from which to select ensemble components.
        For Train/Validate scenario, this parameter should contain a list of Pipelines
        For CrossValidation scenarios, this parameter should contain a list of lists of Pipelines
        (each list will contain the cross validated pipelines)
    :param validation_data: Dataset(s) used for score computation (models have not been trained on them).
        For train/Validate scenario, a single dataset containing X_valid/y_valid is needed.
        For CV case, it should contain the list of the validation sets within each CV fold
    :param metric_to_optimize: The metric to optimize the ensemble selection
    :param class_labels: Applicable only to Classification task, the list of class labels from the entire dataset
    :param y_transformer: Applicable only to Classification task, if necessary
    :param y_min: Applicable only to Regression tasks, the minimum target value
    :param y_max: Applicable only to Regression tasks, the maximum target value
    :param selection_iterations: Represents how many iterations should the selection algorithm be executed

    :return: A tuple containing:
                 The list of indices for the models that have been chosen to be part of the ensemble
                 The list of weights associated to each model that has been chosen.
    """
    selector = EnsembleSelector(
        task_type=task_type,
        training_type=training_type,
        fitted_models=fitted_models,
        validation_data=validation_data,
        metric=metric_to_optimize,
        class_labels=class_labels,
        y_transformer=y_transformer,
        y_min=y_min,
        y_max=y_max,
        selection_iterations=selection_iterations)
    selector.select()
    return selector
