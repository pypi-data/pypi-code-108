# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for computing model evaluation metrics."""
import logging
import datetime

import numpy as np
import pandas as pd

from typing import Any, List, Optional, Union, Dict, Tuple, Callable

import azureml.dataprep as dprep

from azureml._tracing._tracer_factory import get_tracer
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared.constants import Tasks, TrainingResultsType
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import PredictionException
from azureml.automl.runtime import _ml_engine
from azureml.automl.runtime.shared import forecasting_utils
from azureml.automl.runtime.shared.score import _scoring_utilities
from .score import scoring, constants as scoring_constants


logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


def pad_predictions(y_pred_probs: np.ndarray,
                    train_labels: Optional[np.ndarray],
                    class_labels: Optional[np.ndarray]) -> np.ndarray:
    """This function is deprecated."""
    logging.warning("azureml.automl.runtime.shared.metrics_utilities.pad_predictions is deprecated "
                    "and will be removed in a future version of the AzureML SDK")

    return _scoring_utilities.pad_predictions(y_pred_probs, train_labels, class_labels)


def predict_and_compute_metrics_expr_store(
    X_test,
    y_test,
    X_train,
    y_train,
    model,
    task,
    metrics,
    use_binary_metrics=False,
    sample_weight=None,
    problem_info=None,
    enable_metric_confidence=False,
    positive_label=None,
    confidence_metrics=None
):
    """Predict on the test set and compute model evaluation metrics.

    :param X_test: The inputs to test/compute metrics.
    :param y_test: The targets to test/compute metrics.
    :param X_train: The inputs which were used to train the model.
    :param y_train: The targets which were used to train the model.
    :param model: The model to make predictions.
    :param task: The task type (see constants.py).
    :param metrics: The metrics to compute.
    :param use_binary_metrics: Compute metrics on only the second class for binary classification.
        This is usually the true class (when labels are 0 and 1 or false and true).
    :param sample_weight: The weights for each sample to use when computing the score for each metric.
    :param problem_info: The ProblemInfo object used for the run.
    :param enable_metric_confidence: Used to score confidence intervals while computing metrics
    :param positive_label: class designed as positive class in binary classification metrics.
    :param confidence_metrics: The list of metrics to compute confidence interval.
        If None, it will take the value of `metrics`
        If not None, must be a subset of `metrics`.
        metrics in this list but not in `metircs` will be ignored
    :return: A dictionary of metric name -> score.
    """
    Contract.assert_true(task in [Tasks.CLASSIFICATION, Tasks.REGRESSION],
                         "Unsupported task type {}".format(task),
                         target="predict_and_compute_metrics_expr_store", log_safe=False)

    with tracer.start_as_current_span(
            constants.TelemetryConstants.SPAN_FORMATTING.format(
                constants.TelemetryConstants.COMPONENT_NAME, constants.TelemetryConstants.VALIDATION
            ),
            user_facing_name=constants.TelemetryConstants.VALIDATION_USER_FACING
    ):
        # Call predict on the model
        predict_start_time = datetime.datetime.utcnow()
        y_pred = predict(task, model, X_test)
        predict_time = datetime.datetime.utcnow() - predict_start_time

        # Compute model evaluation metrics
        scores = compute_metrics_expr_store(
            X_test,
            y_test,
            X_train,
            y_train,
            y_pred,
            model,
            task,
            metrics,
            use_binary_metrics,
            sample_weight=sample_weight,
            problem_info=problem_info,
            enable_metric_confidence=enable_metric_confidence,
            positive_label=positive_label,
            confidence_metrics=confidence_metrics
        )

        # Add predict time to scores
        scores[TrainingResultsType.PREDICT_TIME] = predict_time.total_seconds()
        return scores


def predict(task, model, X_test):
    """
    Return predictions from the given model with a provided task type.

    :param task: The task type (see constants.py).
    :param model: The model used to make predictions.
    :param X_test: The inputs on which to predict.
    :return: The predictions of the model on X_test
        The shape of the array returned depends on the task type
        Classification will return probabilities for each class.
    """
    with log_utils.log_activity(logger, activity_name=constants.TelemetryConstants.PREDICT_NAME):
        if task == Tasks.CLASSIFICATION:
            y_pred = model.predict_proba(X_test)
        elif task == Tasks.REGRESSION:
            y_pred = model.predict(X_test)
        else:
            raise NotImplementedError

        # Some pipelines will fail silently by predicting NaNs
        # E.g. a pipeline with a preprocessor that does not normalize and a linear model
        #   Pipeline[SVD, SGD] will fail if the dataset contains features on vastly different scales
        # Task to fix for ID features: 550564
        if np.issubdtype(y_pred.dtype, np.number):
            if np.isnan(y_pred).any():
                error_message = ("Silent failure occurred during prediction. "
                                 "This could be a result of unusually large values in the dataset. "
                                 "Normalizing numeric features might resolve this.")
                raise PredictionException.create_without_pii(error_message)

        return y_pred


def compute_metrics_expr_store(
    X_test,
    y_test,
    X_train,
    y_train,
    y_pred,
    model,
    task,
    metrics,
    use_binary_metrics=False,
    sample_weight=None,
    problem_info=None,
    enable_metric_confidence=False,
    positive_label=None,
    confidence_metrics=None
):
    """Compute model evaluation metrics.

    :param X_test: The inputs which were used to compute the predictions.
    :param y_test: The targets of the test set.
    :param X_train: The inputs which were used to train the model.
    :param y_train: The targets which were used to train the model.
    :param y_pred: The predicted values.
    :param model: The model which was used to make predictions.
    :param task: The task type (see constants.py).
    :param metrics: The metrics that will be computed.
    :param use_binary_metrics: Compute metrics on only the second class for binary classification.
        This is usually the true class (when labels are 0 and 1 or false and true).
    :param sample_weight: The weights for each sample to use when computing the score for each metric.
    :param problem_info: The ProblemInfo object used for the run.
    :param enable_metric_confidence: Used to score confidence intervals while computing metrics
    :param positive_label: class designed as positive class in binary classification metrics.
    :param confidence_metrics: The list of metrics to compute confidence interval.
        If None, it will take the value of `metrics`
        If not None, must be a subset of `metrics`.
        metrics in this list but not in `metircs` will be ignored
    :return: A dictionary of metric name -> score.
    """
    with log_utils.log_activity(logger, activity_name=constants.TelemetryConstants.COMPUTE_METRICS_NAME):
        expr_store = ExperimentStore.get_instance()
        # if y_test is a Dataflow, convert it to a numpy array
        # (we are assuming that y_test is small enough to fit into memory)
        if isinstance(y_test, dprep.Dataflow):
            y_test = y_test.to_pandas_dataframe(on_error='null').iloc[:, 0].values

        # if sample_weight is a Dataflow, convert it to a numpy array
        # (we are assuming that sample_weight is small enough to fit into memory)
        if isinstance(sample_weight, dprep.Dataflow):
            sample_weight = sample_weight.to_pandas_dataframe(on_error='null').iloc[:, 0].values

        if task == Tasks.CLASSIFICATION:
            y_transformer = expr_store.transformers.get_y_transformer()
            class_labels = get_class_labels_expr_store()
            train_labels = get_trained_labels_expr_store(model, y_train=y_train, problem_info=problem_info)

            # ensure that labels sent into metrics code are numeric or string
            if not np.issubdtype(y_test.dtype, np.number):
                y_test = y_test.astype(str)
                class_labels = class_labels.astype(str)
                train_labels = train_labels.astype(str)

            # Remove empty string labels because NimbusML/ML.NET ignores them when
            # reporting predict_proba for classification tasks
            train_labels = np.array([label for label in train_labels if label != '' and label is not None])

            if isinstance(y_pred, pd.DataFrame):
                y_pred = y_pred.values

            scores = _ml_engine.evaluate_classifier(
                y_test, y_pred, metrics, class_labels, train_labels,
                sample_weight=sample_weight, y_transformer=y_transformer,
                use_binary=use_binary_metrics, enable_metric_confidence=enable_metric_confidence,
                confidence_metrics=confidence_metrics, positive_label=positive_label
            )
        else:
            y_min, y_max = expr_store.metadata.regression.get_y_range()
            bin_info = expr_store.metadata.regression.bin_info

            y_std = None
            if problem_info is None or not problem_info.enable_streaming:
                y_std = expr_store.metadata.regression.y_std

            metrics_regression = [m for m in list(scoring_constants.REGRESSION_SET) if m in metrics]

            # Post-processing for y is applied here
            y_transformer = expr_store.transformers.get_y_transformer()
            if(y_transformer is not None):
                y_pred = y_transformer.inverse_transform(y_pred)
                y_test = y_transformer.inverse_transform(y_test)

            scores = _ml_engine.evaluate_regressor(
                y_test, y_pred, metrics_regression,
                y_min=y_min, y_max=y_max, y_std=y_std,
                bin_info=bin_info,
                sample_weight=sample_weight,
                enable_metric_confidence=enable_metric_confidence,
                confidence_metrics=confidence_metrics)

            if expr_store.metadata.is_timeseries:
                # Retrieve the forecasting metrics.
                metrics_forecasting = [m for m in list(scoring_constants.FORECASTING_SET) if m in metrics]

                transformation_pipeline = expr_store.transformers.get_timeseries_transformer()
                grain_column_names = transformation_pipeline.grain_column_names
                time_column_name = transformation_pipeline.time_column_name
                engineered_feature_names = transformation_pipeline.get_engineered_feature_names()

                # retrieve horizons for horizon aware metrics
                try:
                    if isinstance(X_test, pd.DataFrame):
                        horizons = X_test[constants.TimeSeriesInternal.HORIZON_NAME].values
                    else:
                        horizon_idx = engineered_feature_names.index(constants.TimeSeriesInternal.HORIZON_NAME)
                        horizons = X_test[:, horizon_idx]
                except (KeyError, ValueError):
                    # If no horizon is present we are doing a basic forecast.
                    # The model's error estimation will be based on the overall
                    # stddev of the errors, multiplied by a factor of the horizon.
                    horizons = np.repeat(None, y_pred.shape[0])

                additional_scores = _ml_engine.evaluate_timeseries(
                    y_test, y_pred, metrics_forecasting, horizons,
                    y_min=y_min, y_max=y_max, y_std=y_std,
                    bin_info=bin_info,
                    sample_weight=sample_weight,
                    X_test=X_test, X_train=X_train, y_train=y_train,
                    grain_column_names=grain_column_names,
                    time_column_name=time_column_name)
                scores.update(additional_scores)

                # Update normalized metrics to be normalized by grain.
                # if the place holder grain column is in grain column lists we have a single grain
                # and can skip the update.
                if constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN not in grain_column_names:
                    agg_norm_by_grain = compute_normalized_metrics_forecasting_by_grain(
                        X_train,
                        y_train,
                        X_test,
                        y_test,
                        y_pred,
                        metrics,
                        sample_weight,
                        transformation_pipeline
                    )
                    scores.update(agg_norm_by_grain)
    return scores


def predict_and_compute_metrics(X_test,
                                y_test,
                                X_train,
                                y_train,
                                model,
                                dataset,
                                task,
                                metrics,
                                use_binary_metrics=False,
                                sample_weight=None,
                                problem_info=None,
                                enable_metric_confidence=False):
    """Predict on the test set and compute model evaluation metrics.

    NOTE: This method is used by Miro only and must be maintained for backwards compatibility.


    :param X_test: The inputs to test/compute metrics.
    :param y_test: The targets to test/compute metrics.
    :param X_train: The inputs which were used to train the model.
    :param y_train: The targets which were used to train the model.
    :param model: The model to make predictions.
    :param dataset: ClientDataset object that contains information about the dataset (see datasets.py).
    :param task: The task type (see constants.py).
    :param metrics: The metrics to compute.
    :param use_binary_metrics: Compute metrics on only the second class for binary classification.
        This is usually the true class (when labels are 0 and 1 or false and true).
    :param sample_weight: The weights for each sample to use when computing the score for each metric.
    :param problem_info: The ProblemInfo object used for the run.
    :param enable_metric_confidence: Used to score confidence intervals while computing metrics
    :return: A dictionary of metric name -> score.
    """
    Contract.assert_true(task in [Tasks.CLASSIFICATION, Tasks.REGRESSION],
                         "Unsupported task type {}".format(task),
                         target="predict_and_compute_metrics", log_safe=False)

    with tracer.start_as_current_span(
            constants.TelemetryConstants.SPAN_FORMATTING.format(
                constants.TelemetryConstants.COMPONENT_NAME, constants.TelemetryConstants.VALIDATION
            ),
            user_facing_name=constants.TelemetryConstants.VALIDATION_USER_FACING
    ):
        # Call predict on the model
        predict_start_time = datetime.datetime.utcnow()
        y_pred = predict(task, model, X_test)
        predict_time = datetime.datetime.utcnow() - predict_start_time

        # Compute model evaluation metrics
        scores = compute_metrics(X_test,
                                 y_test,
                                 X_train,
                                 y_train,
                                 y_pred,
                                 model, dataset,
                                 task,
                                 metrics,
                                 use_binary_metrics,
                                 sample_weight=sample_weight,
                                 problem_info=problem_info,
                                 enable_metric_confidence=enable_metric_confidence)

        # Add predict time to scores
        scores[TrainingResultsType.PREDICT_TIME] = predict_time.total_seconds()
        return scores


def compute_metrics(X_test,
                    y_test,
                    X_train,
                    y_train,
                    y_pred,
                    model,
                    dataset,
                    task,
                    metrics,
                    use_binary_metrics=False,
                    sample_weight=None,
                    problem_info=None,
                    enable_metric_confidence=False):
    """Compute model evaluation metrics.

    NOTE: This method is used by Miro only and must be maintained for backwards compatibility.

    :param X_test: The inputs which were used to compute the predictions.
    :param y_test: The targets of the test set.
    :param X_train: The inputs which were used to train the model.
    :param y_train: The targets which were used to train the model.
    :param y_pred: The predicted values.
    :param model: The model which was used to make predictions.
    :param dataset: ClientDataset object that contains information about the dataset (see datasets.py).
    :param task: The task type (see constants.py).
    :param metrics: The metrics that will be computed.
    :param use_binary_metrics: Compute metrics on only the second class for binary classification.
        This is usually the true class (when labels are 0 and 1 or false and true).
    :param sample_weight: The weights for each sample to use when computing the score for each metric.
    :param problem_info: The ProblemInfo object used for the run.
    :param enable_metric_confidence: Used to score confidence intervals while computing metrics
    :return: A dictionary of metric name -> score.
    """
    with log_utils.log_activity(logger, activity_name=constants.TelemetryConstants.COMPUTE_METRICS_NAME):
        # if y_test is a Dataflow, convert it to a numpy array
        # (we are assuming that y_test is small enough to fit into memory)
        if isinstance(y_test, dprep.Dataflow):
            y_test = y_test.to_pandas_dataframe(on_error='null').iloc[:, 0].values

        # if sample_weight is a Dataflow, convert it to a numpy array
        # (we are assuming that sample_weight is small enough to fit into memory)
        if isinstance(sample_weight, dprep.Dataflow):
            sample_weight = sample_weight.to_pandas_dataframe(on_error='null').iloc[:, 0].values

        if task == Tasks.CLASSIFICATION:
            y_transformer = dataset.get_y_transformer()
            class_labels = get_class_labels(dataset)
            train_labels = get_trained_labels(model, y_train=y_train,
                                              dataset=dataset, problem_info=problem_info)

            # ensure that labels sent into metrics code are numeric or string
            if not np.issubdtype(y_test.dtype, np.number):
                y_test = y_test.astype(str)
                class_labels = class_labels.astype(str)
                train_labels = train_labels.astype(str)

            # Remove empty string labels because NimbusML/ML.NET ignores them when
            # reporting predict_proba for classification tasks
            train_labels = np.array([label for label in train_labels if label != '' and label is not None])

            if isinstance(y_pred, pd.DataFrame):
                y_pred = y_pred.values

            scores = _ml_engine.evaluate_classifier(
                y_test, y_pred, metrics, class_labels, train_labels,
                sample_weight=sample_weight, y_transformer=y_transformer,
                use_binary=use_binary_metrics, enable_metric_confidence=enable_metric_confidence)
        else:
            y_min, y_max = dataset.get_y_range()
            bin_info = dataset.get_bin_info()

            y_std = None
            if problem_info is None or not problem_info.enable_streaming:
                y_std = dataset.get_y_std()

            metrics_regression = [m for m in list(scoring_constants.REGRESSION_SET) if m in metrics]

            # Post-processing for y is applied here
            if(dataset.get_y_transformer() is not None):
                y_transformer = dataset.get_y_transformer()
                y_pred = y_transformer.inverse_transform(y_pred)
                y_test = y_transformer.inverse_transform(y_test)

            scores = _ml_engine.evaluate_regressor(
                y_test, y_pred, metrics_regression,
                y_min=y_min, y_max=y_max, y_std=y_std,
                bin_info=bin_info,
                sample_weight=sample_weight,
                enable_metric_confidence=enable_metric_confidence)

            if dataset.is_timeseries():
                # Retrieve the forecasting metrics.
                metrics_forecasting = [m for m in list(scoring_constants.FORECASTING_SET) if m in metrics]

                transformation_pipeline = dataset.get_transformer(constants.Transformers.TIMESERIES_TRANSFORMER)
                grain_column_names = transformation_pipeline.grain_column_names
                time_column_name = transformation_pipeline.time_column_name
                engineered_feature_names = transformation_pipeline.get_engineered_feature_names()

                # retrieve horizons for horizon aware metrics
                try:
                    if isinstance(X_test, pd.DataFrame):
                        horizons = X_test[constants.TimeSeriesInternal.HORIZON_NAME].values
                    else:
                        horizon_idx = engineered_feature_names.index(constants.TimeSeriesInternal.HORIZON_NAME)
                        horizons = X_test[:, horizon_idx]
                except (KeyError, ValueError):
                    # If no horizon is present we are doing a basic forecast.
                    # The model's error estimation will be based on the overall
                    # stddev of the errors, multiplied by a factor of the horizon.
                    horizons = np.repeat(None, y_pred.shape[0])

                additional_scores = _ml_engine.evaluate_timeseries(
                    y_test, y_pred, metrics_forecasting, horizons,
                    y_min=y_min, y_max=y_max, y_std=y_std,
                    bin_info=bin_info,
                    sample_weight=sample_weight,
                    X_test=X_test, X_train=X_train, y_train=y_train,
                    grain_column_names=grain_column_names,
                    time_column_name=time_column_name)
                scores.update(additional_scores)

                # Update normalized metrics to be normalized by grain.
                # if the place holder grain column is in grain column lists we have a single grain
                # and can skip the update.
                if constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN not in grain_column_names:
                    agg_norm_by_grain = compute_normalized_metrics_forecasting_by_grain(
                        X_train,
                        y_train,
                        X_test,
                        y_test,
                        y_pred,
                        metrics,
                        sample_weight,
                        transformation_pipeline
                    )
                    scores.update(agg_norm_by_grain)
    return scores


def get_class_labels(dataset):
    """
    Get the full set of class labels from the dataset.

    NOTE: This method is used by Miro only and must be maintained for backwards compatibility.

    Sometimes the class_labels attribute is not set on the ClientDatasets object if the
    object is constructed with the meta_data parameter. In this case we need to compute
    the unique labels by hand in order to compute metrics.

    :param dataset: The DatasetBase object that contains information about the dataset.
    :return: The labels from the full dataset.
    """
    class_labels = dataset.get_class_labels()
    if class_labels is not None:
        return class_labels
    _, y, _ = dataset.get_full_set()
    return np.unique(y[~np.isnan(y)])


def get_trained_labels(model, y_train=None, dataset=None, problem_info=None):
    """
    Return the class labels that a model has been trained on.

    NOTE: This method is used by Miro only and must be maintained for backwards compatibility.

    Sometimes a model is only trained on a subset of the class labels from
    the dataset. This is especially common with cross validation and
    custom validation sets. This function returns the class labels that
    a model has been trained on.
    If the model is a regression model the function returns np.unique of y_train,
    but this function shouldn't be used for regression
    :param model: The model used to make predictions.
    :param y_train: Targets used during model training.
    :param dataset: The DatasetBase object that contains information about the dataset.
    :param problem_info: The ProblemInfo object used for the run.
    :return: The labels used when training the model.
    """
    if hasattr(model, "classes_"):
        if model.classes_ is None:
            logger.warning("AutoML classification model found with classes_ set to None")
        else:
            return model.classes_
    else:
        logger.warning("AutoML classification model found without classes_ attribute")

    if problem_info is not None and problem_info.enable_streaming and dataset is not None:
        return dataset.get_train_class_labels()

    # This should have been earlier in the validation stack, hence a System error.
    # If this is being raised, the bug is elsewhere! Remove this line once / if we hit this exception.
    Contract.assert_true(y_train is not None,
                         message="y_train must be passed if the model does not support the classes_ attribute",
                         target="y_train", log_safe=True)

    return np.unique(y_train)


def get_class_labels_expr_store():
    """
    Get the full set of class labels from the ExperimentStore.

    Sometimes the class_labels attribute is not set on the ExperimentStore's Metadata.
    In this case we need to compute the unique labels by hand in order to compute metrics.

    :return: The labels from the full dataset stored in the ExperimentStore.
    """
    expr_store = ExperimentStore.get_instance()
    class_labels = expr_store.metadata.classification.class_labels
    if class_labels is not None:
        return class_labels
    _, y, _ = expr_store.data.materialized.get_train()
    return np.unique(y[~np.isnan(y)])


def get_trained_labels_expr_store(model, y_train=None, problem_info=None):
    """
    Return the class labels that a model has been trained on.

    Sometimes a model is only trained on a subset of the class labels from
    the dataset. This is especially common with cross validation and
    custom validation sets. This function returns the class labels that
    a model has been trained on.
    If the model is a regression model the function returns np.unique of y_train,
    but this function shouldn't be used for regression.
    :param model: The model used to make predictions.
    :param y_train: Targets used during model training.
    :param problem_info: The ProblemInfo object used for the run.
    :return: The labels used when training the model.
    """
    if hasattr(model, "classes_"):
        if model.classes_ is None:
            logger.warning("AutoML classification model found with classes_ set to None")
        else:
            return model.classes_
    else:
        logger.warning("AutoML classification model found without classes_ attribute")

    # This should have been earlier in the validation stack, hence a System error.
    # If this is being raised, the bug is elsewhere! Remove this line once / if we hit this exception.
    Contract.assert_true(y_train is not None,
                         message="y_train must be passed if the model does not support the classes_ attribute",
                         target="y_train", log_safe=True)

    return np.unique(y_train)


def compute_normalized_metrics_forecasting_by_grain(
    X_train: Union[np.ndarray, pd.DataFrame],
    y_train: Union[np.ndarray, dprep.Dataflow],
    X_valid: Union[np.ndarray, pd.DataFrame],
    y_valid: Union[np.ndarray, dprep.Dataflow],
    y_pred: np.ndarray,
    metrics: List[str],
    sample_weight: Optional[np.ndarray],
    transformation_pipeline: Any,
) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute metrics normalized metrics by grain.

    Compute metrics which should be normalized per grain rather than over the entire dataset.
    Average metrics after normalization.

    :param X_train: The featurized training data.
    :param y_train: The featurized training target.
    :param X_valid: The featurized validation data.
    :param y_valid: The featurized validation target.
    :param y_pred: The predicted target from the model.
    :param metrics: The metrics to compute.
    :parm sample_weight: The sample_weights to be used for validation.
    :param transformation_pipeline: The fitted timeseriestransformer used to featurize X & y.
    """
    # Retrieve metrics which are normalized and require grain aware calculations.
    normalized_metrics_forecasting =\
        [m for m in list(scoring_constants.REGRESSION_NORMALIZED_SET) if m in metrics]

    grain_column_names = transformation_pipeline.grain_column_names

    validation_grains = get_grains_from_data(X_valid, grain_column_names, transformation_pipeline)
    training_grains = get_grains_from_data(X_train, grain_column_names, transformation_pipeline)

    full_grains = np.concatenate((training_grains, validation_grains))
    full_y = np.concatenate((y_train, y_valid))
    df_full = pd.DataFrame(full_grains)
    target_col = 'target'
    df_full[target_col] = full_y

    min_max = {}
    for k, grp in df_full.groupby(list(range(0, len(grain_column_names)))):
        min_max[k] = (grp[target_col].min(), grp[target_col].max())

    norm_by_grain = compute_by_group(
        y_valid, y_pred, validation_grains, min_max,
        scoring.score_regression,
        metrics=normalized_metrics_forecasting,
        sample_weight=sample_weight)

    return scoring.aggregate_scores(
        [norm_by_grain[key] for key in norm_by_grain.keys()],
        normalized_metrics_forecasting
    )


def get_grains_from_data(data, grain_column_names, tranformation_pipeline):
    """
    Get grains from data.

    :param data: The featurized data. This can be a dataframe or ndarray.
    :param grain_column_names: A list of grain_column_names used to train the model.
    :param transformation_pipeline: The timeseriestransformer used to featurize the data.
    """
    # In the case of a df, we know the grain columns are either all in the index or all in the columns
    if isinstance(data, pd.DataFrame):
        if all(tsid_col in data.index.names for tsid_col in grain_column_names):
            grain_dict = {tsid_col: data.index.get_level_values(tsid_col) for tsid_col in grain_column_names}
            grains = pd.DataFrame(grain_dict).values
        else:
            grains = data[grain_column_names].values
    # otherwise, we need to retrieve the grain column names from the grain_index_featurizer
    # and get the indices of the feautrized data with grain columns.
    else:
        # convert grain columns to featurized grain column names
        featurized_grain_column_names = forecasting_utils.get_pipeline_step(
            tranformation_pipeline.pipeline,
            constants.TimeSeriesInternal.MAKE_GRAIN_FEATURES
        )._preview_grain_feature_names_from_grains(grain_column_names)

        engineered_feature_names = tranformation_pipeline.get_engineered_feature_names()
        grain_col_indices = []
        # get the index of each grain column
        for col in featurized_grain_column_names:
            grain_col_indices.append(engineered_feature_names.index(col))
        grains = data[:, grain_col_indices]

    return grains


def compute_by_group(
    y_test: np.ndarray,
    y_pred: np.ndarray,
    group_by_columns: np.ndarray,
    min_max: Optional[Dict[Any, Tuple[float, float]]],
    partial_func: Callable[..., Dict[str, Any]],
    **partial_func_kwargs: Any
) -> Dict[Any, Dict[str, List[float]]]:
    """
    Group y_true and y_pred by group name.

    :param y_test: Actual targets.
    :param y_pred: Predicted targets.
    :param group_by_columns: ndarray of column(s) with to be used as group indicators.
    :param min_max: A dict of group keys to min, max tuples.
    :param partial_func: Function that takes y_test/y_pred
        and returns a result dict for some group of samples.
        This should be a call to the score_<task> method,
        ensuring the kwargs match the signature.
    :param partial_func_kwargs: Keyword arguments needed to call partial_func.
    :return: A dictionary of group name -> result.
    """
    # groupby columns will be named 0 to n-1
    df = pd.DataFrame(group_by_columns)
    num_cols = df.shape[1]
    df['y_test'] = y_test
    df['y_pred'] = y_pred

    # ensure sample weight is grouped by metric
    SAMPLE_WEIGHT = 'sample_weight'
    sample_weights = False
    if partial_func_kwargs.get(SAMPLE_WEIGHT):
        sample_weights = True
        df[SAMPLE_WEIGHT] = partial_func_kwargs[SAMPLE_WEIGHT]
        partial_func_kwargs.pop(SAMPLE_WEIGHT)

    score_data = dict()
    for key, group in df.groupby(list(range(0, num_cols))):
        if min_max is not None:
            y_min, y_max = min_max[key]
            partial_func_kwargs['y_min'] = y_min
            partial_func_kwargs['y_max'] = y_max

        if sample_weights:
            partial_func_kwargs[SAMPLE_WEIGHT] = group[SAMPLE_WEIGHT]

        score_data[key] = partial_func(group['y_test'], group['y_pred'], **partial_func_kwargs)
    return score_data
