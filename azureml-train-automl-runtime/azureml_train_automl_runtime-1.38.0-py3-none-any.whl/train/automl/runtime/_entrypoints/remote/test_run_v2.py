# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods for AutoML remote runs."""
import logging
from datetime import datetime
import numpy as np
import mlflow
from typing import Any, List, Optional

from azureml._tracing import get_tracer
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.shared import constants
from azureml.automl.core.shared.telemetry_activity_logger import TelemetryActivityLogger
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.shared.memory_cache_store import MemoryCacheStore
from azureml.core import Run
from azureml.core.dataset import Dataset
from azureml.train.automl.run import AutoMLRun
from azureml.train.automl.runtime._automl_job_phases import ModelTestPhase
from azureml.train.automl.utilities import _get_package_version
from azureml.train.automl.runtime import _model_test_utilities
from azureml.train.automl.runtime._entrypoints import entrypoint_util

logger = logging.getLogger(__name__)
activity_logger = TelemetryActivityLogger()
tracer = get_tracer(__name__)


def _set_expr_store(
        task,
        y,
        y_transformer,
        transformation_pipeline):
    # Create a new cache store for this TSI run
    expr_store = ExperimentStore(MemoryCacheStore(), read_only=False)
    if task == "classification":
        expr_store.metadata.classification.class_labels = np.unique(y)
        expr_store.metadata.classification.num_classes = len(expr_store.metadata.classification.class_labels)
    else:
        expr_store.metadata.regression.y_min = min(y)
        expr_store.metadata.regression.y_max = max(y)
        expr_store.metadata.regression.y_std = y.std()
        # bin info?
    expr_store.transformers.set_transformers({
        constants.Transformers.Y_TRANSFORMER: y_transformer,
        constants.Transformers.TIMESERIES_TRANSFORMER: transformation_pipeline
    })


def execute(
        script_directory: str,
        train_dataset: Optional[Dataset],
        test_dataset: Dataset,
        label_column_name: str,
        model_id: str,
        entry_point: str,
        y_transformer: Optional[Any] = None,
        transformation_pipeline: Optional[Any] = None,
        task: str = "classification",
        automl_run_id: Optional[str] = None,
        **kwargs: Any
) -> None:
    """
    Run the Model Test Phase to calculate metrics on a trained model using a test set.

    :param script_directory: Unused common parameter for phases.
    :param train_dataset: The original training dataset for this model.
    :param test_dataset: The test dataset to use to calculate metrics.
    :param label_column_name: The label column name for these datasets.
    :param model_id: The MLFlow model id for the model to be evaluated.
    :param entry_point: Unused common parameter for phases.
    :param y_transformer: The y_transformer to use for this phase. This is loaded from the cache store
        for AutoML runs.
    :param transformation_pipeline: The transformation pipeline for forecasting. This is loaded from the cache store
        for AutoML runs.
    :param task: What type of model is being evaluated: classification, regression, or forecasting.
    :param automl_run_id: The run id for an AutoML run. This is used to load the cache store.
    :param kwargs:
    :return:
    """
    current_run = Run.get_context()

    pkg_ver = _get_package_version()
    logger.info(f'Using SDK version {pkg_ver}')

    try:
        print(f"{datetime.now().__format__('%Y-%m-%d %H:%M:%S,%f')} - INFO - Beginning model test wrapper.")
        mlflow.set_tracking_uri(current_run.experiment.workspace.get_mlflow_tracking_uri())

        if automl_run_id:
            use_fd_cache = False
            automl_settings_obj = AutoMLRun(current_run.experiment, automl_run_id)._get_automl_settings()
            if hasattr(automl_settings_obj, "use_fd_cache"):
                use_fd_cache = True
            cache_store = entrypoint_util.init_cache_store(
                current_run.experiment,
                parent_run_id=automl_run_id,
                use_fd_cache=use_fd_cache
            )
            cache_store.load()
            expr_store = ExperimentStore(cache_store, read_only=True)
            expr_store.load()
            X, y, _ = expr_store.data.materialized.get_train()
        else:
            X, y = _model_test_utilities.get_X_y_from_dataset_label(train_dataset, label_column_name)
            _set_expr_store(
                task,
                y,
                y_transformer,
                transformation_pipeline)

        X_test, y_test = _model_test_utilities.get_X_y_from_dataset_label(test_dataset, label_column_name)

        is_timeseries = False
        if task.lower() == "forecasting":
            task = "regression"
            is_timeseries = True

        # y_context should be None for TSI
        y_context = None

        ModelTestPhase.run(
            model=model_id,
            test_run=current_run,
            X_train=X,
            y_train=y,
            X_test=X_test,
            y_test=y_test,
            y_context=y_context,
            label_column_name=label_column_name,
            task=task,
            is_timeseries=is_timeseries,
            test_include_predictions_only=False)
    except Exception as e:
        logger.error(f"AutoML test_wrapper script terminated with an exception of type: {type(e)}")
        run_lifecycle_utilities.fail_run(current_run, e)
        raise
    finally:
        ExperimentStore.reset()
