# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods for AutoML remote runs."""
import logging
from typing import Any, Optional, Dict

from azureml._tracing import get_tracer
from azureml.train.automl._azure_experiment_observer import AzureExperimentObserver

from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.constants import FeaturizationRunConstants
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared.telemetry_activity_logger import TelemetryActivityLogger
from azureml.automl.runtime import data_transformation, _data_transformation_utilities
from azureml.automl.runtime._data_transformation_utilities import FeaturizationJsonParser
from azureml.automl.runtime.data_context import RawDataContext, DataContextParams
from azureml.automl.runtime.distributed.utilities import is_master_process
from azureml.automl.runtime.featurization import DataTransformer
from azureml.automl.runtime.featurization._featurizer_container import FeaturizerContainer
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.core import Run
from azureml.train.automl.runtime._entrypoints import entrypoint_util, featurization_entrypoint_util
from azureml.automl.core._experiment_observer import ExperimentObserver

logger = logging.getLogger(__name__)
activity_logger = TelemetryActivityLogger()
tracer = get_tracer(__name__)


def execute(
        script_directory: Optional[str],
        dataprep_json: str,
        entry_point: str,
        automl_settings: str,
        setup_container_id: str,
        featurization_json: str,
        **kwargs: Any) -> None:
    """
    Code for fitting individual featurizer(s) as a part of the featurization iteration for AutoML remote runs.
    """
    fit_featurizer_run = Run.get_context()
    parent_run, automl_settings_obj, cache_store = entrypoint_util.init_wrapper(
        fit_featurizer_run, automl_settings, script_directory)
    ExperimentStore(cache_store, read_only=False)
    property_dict = fit_featurizer_run.get_properties()

    featurization_entrypoint_util.transfer_files_from_setup(fit_featurizer_run, setup_container_id,
                                                            property_dict.get(FeaturizationRunConstants.CONFIG_PROP,
                                                                              FeaturizationRunConstants.CONFIG_PATH),
                                                            property_dict.get(FeaturizationRunConstants.NAMES_PROP,
                                                                              FeaturizationRunConstants.NAMES_PATH))
    try:
        experiment_observer = AzureExperimentObserver(parent_run)
        raw_experiment_data, feature_config_manager = \
            featurization_entrypoint_util.initialize_data(
                fit_featurizer_run, "individual featurizer", automl_settings_obj, script_directory, dataprep_json,
                entry_point, parent_run.id)

        raw_data_context = RawDataContext(DataContextParams(automl_settings_obj),
                                          X=raw_experiment_data.X,
                                          y=raw_experiment_data.y,
                                          X_valid=raw_experiment_data.X_valid,
                                          y_valid=raw_experiment_data.y_valid,
                                          sample_weight=raw_experiment_data.weights,
                                          sample_weight_valid=raw_experiment_data.weights_valid,
                                          x_raw_column_names=raw_experiment_data.feature_column_names,
                                          cv_splits_indices=raw_experiment_data.cv_splits_indices,
                                          training_data=raw_experiment_data.training_data,
                                          validation_data=raw_experiment_data.validation_data,
                                          data_snapshot_str=raw_experiment_data.data_snapshot_str
                                          )

        feature_sweeping_config = feature_config_manager.get_feature_sweeping_config(
            enable_feature_sweeping=automl_settings_obj.enable_feature_sweeping,
            parent_run_id=parent_run.id,
            task_type=automl_settings_obj.task_type)

        featurizer_container = FeaturizationJsonParser.parse_featurizer_container(
            featurization_json,
            is_onnx_compatible=automl_settings_obj.enable_onnx_compatible_models)

        logger.info("Beginning to fit and cache specified featurizers.")
        fit_and_cache_featurizers(
            raw_data_context=raw_data_context,
            featurizer_container=featurizer_container,
            cache_store=cache_store,
            observer=experiment_observer,
            is_onnx_compatible=automl_settings_obj.enable_onnx_compatible_models,
            enable_feature_sweeping=automl_settings_obj.enable_feature_sweeping,
            enable_dnn=automl_settings_obj.enable_dnn,
            force_text_dnn=automl_settings_obj.force_text_dnn,
            feature_sweeping_config=feature_sweeping_config,
            enable_categorical_indicators=automl_settings_obj.enable_categorical_indicators
        )
    except Exception as e:
        logger.error("AutoML featurizer fitting script terminated with an exception of type: {}".format(type(e)))
        run_lifecycle_utilities.fail_run(fit_featurizer_run, e, update_run_properties=True)
        raise
    finally:
        # Reset the singleton for subsequent usage.
        ExperimentStore.reset()


def fit_and_cache_featurizers(raw_data_context: RawDataContext,
                              featurizer_container: FeaturizerContainer,
                              cache_store: CacheStore,
                              observer: Optional[ExperimentObserver] = None,
                              is_onnx_compatible: bool = False,
                              enable_feature_sweeping: bool = False,
                              enable_dnn: bool = False,
                              force_text_dnn: bool = False,
                              feature_sweeping_config: Optional[Dict[str, Any]] = None,
                              working_dir: Optional[str] = None,
                              enable_categorical_indicators: bool = False) -> None:
    """
    Fit and cache individual featurizers. Designed to be called in a separate run from the rest of
    data transformation, so the fitted featurizers must be cached after being fitted.

    :param raw_data_context: The raw input data.
    :param featurizer_container: The featurization JSON that we will use to determine which featurizers to fit.
    :param cache_store: The object that should be used to cache featurized data.
    :param observer: The experiment observer.
    :param is_onnx_compatible: If works in onnx compatible mode.
    :param enable_feature_sweeping: Enable or disable feature sweeping.
    :param enable_dnn: Flag to enable neural networks for forecasting and natural language processing.
    :param force_text_dnn: Flag to force add neural networks for natural language processing in feature sweeping.
    :param feature_sweeping_config: Config used for feature sweeping.
    :param working_dir: Working directory to use for featurization/training.
    :return: None. The results are cached.

    Note that the last six parameters will be condensed into a DataTransformerSettings object once that PR merges.
    """
    if feature_sweeping_config is None:
        feature_sweeping_config = {}

    # investigate caching these results, since they're used in all the runs.
    transformed_data_context, _, _, _ = \
        data_transformation.create_transformed_data_context_no_streaming(raw_data_context, cache_store)

    # investigate moving this into create_transformed_data_context_no_streaming so we don't have to put it everywhere
    transformed_data_context.X = _data_transformation_utilities._add_raw_column_names_to_X(
        transformed_data_context.X,
        raw_data_context.x_raw_column_names)

    featurization_config = raw_data_context.featurization if isinstance(raw_data_context.featurization,
                                                                        FeaturizationConfig) else None

    data_transformer = DataTransformer(
        task=raw_data_context.task_type,
        is_onnx_compatible=is_onnx_compatible,
        enable_feature_sweeping=enable_feature_sweeping,
        enable_dnn=enable_dnn,
        force_text_dnn=force_text_dnn,
        observer=observer,
        featurization_config=featurization_config,
        is_cross_validation=transformed_data_context._is_cross_validation_scenario(),
        feature_sweeping_config=feature_sweeping_config,
        working_dir=working_dir,
        enable_categorical_indicators=enable_categorical_indicators
    )

    _data_transformation_utilities.load_and_update_from_sweeping(data_transformer, transformed_data_context.X)

    for featurizer in featurizer_container:
        if is_master_process() or featurizer.is_distributable:
            fitted_featurizer = featurizer.fit(
                data_transformer=data_transformer,
                df=transformed_data_context.X,
                y=transformed_data_context.y)
            cache_store.set(
                _data_transformation_utilities.get_cache_key_from_index(featurizer.index),
                fitted_featurizer)
