# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes that group various parameters."""
from typing import Dict, Optional, Union
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.forecasting_parameters import ForecastingParameters
from azureml.automl.runtime import feature_skus_utilities
from azureml.automl.core.shared import utilities


class ExperimentOrchestrationSettings:

    def __init__(self, automl_settings: AutoMLBaseSettings):
        self.iterations = automl_settings.iterations
        self.max_concurrent_iterations = automl_settings.max_concurrent_iterations
        self.iteration_timeout_minutes = automl_settings.iteration_timeout_minutes
        self.experiment_timeout_minutes = automl_settings.experiment_timeout_minutes
        self.experiment_exit_score = automl_settings.experiment_exit_score
        self.enable_early_stopping = automl_settings.enable_early_stopping
        self.early_stopping_n_iters = automl_settings.early_stopping_n_iters
        self.ensemble_iterations = automl_settings.ensemble_iterations
        self.enable_local_managed = automl_settings.enable_local_managed
        self.track_child_runs = automl_settings.track_child_runs


class PipelineSelectionSettings:

    def __init__(self, automl_settings: AutoMLBaseSettings):
        self.blacklist_models = automl_settings.blacklist_algos
        self.whitelist_models = automl_settings.whitelist_models
        self.enable_voting_ensemble = automl_settings.enable_ensembling
        self.enable_stack_ensemble = automl_settings.enable_stack_ensembling
        self.enable_tf = automl_settings.enable_tf
        self.enable_onnx_compatible_models = automl_settings.enable_onnx_compatible_models
        self.enable_split_onnx_featurizer_estimator_models = \
            automl_settings.enable_split_onnx_featurizer_estimator_models
        self.enable_nimbusml = automl_settings.enable_nimbusml
        self.force_streaming = automl_settings.force_streaming
        self.forecasting_parameters = ForecastingParameters.from_parameters_dict(
            automl_settings.__dict__, False, False)
        self.allowed_private_models = automl_settings.allowed_private_models


class ExperimentControlSettings:

    def __init__(self, automl_settings: AutoMLBaseSettings):
        self.task_type = automl_settings.task_type
        self.is_timeseries = automl_settings.is_timeseries
        self.primary_metric = automl_settings.primary_metric
        self.metric_operation = automl_settings.metric_operation
        self.positive_label = automl_settings.positive_label
        self.exclude_nan_labels = automl_settings.exclude_nan_labels
        self.model_explainability = automl_settings.model_explainability
        self.enable_streaming = automl_settings.enable_streaming
        self.enable_subsampling = automl_settings.enable_subsampling
        self.subsample_seed = automl_settings.subsample_seed
        self.cost_mode = automl_settings.cost_mode
        self.enable_feature_sweeping = automl_settings.enable_feature_sweeping
        self.enable_metric_confidence = automl_settings.enable_metric_confidence
        self.save_mlflow = automl_settings.save_mlflow
        self.enable_categorical_indicators = automl_settings.enable_categorical_indicators

        if isinstance(automl_settings.featurization, dict):
            featurization_config = FeaturizationConfig()
            featurization_config._from_dict(automl_settings.featurization)
            self.featurization = featurization_config   # type: Union[str, FeaturizationConfig]
        else:
            self.featurization = automl_settings.featurization

        if getattr(automl_settings, "is_gpu", False):
            self.gpu_training_param_dict = {"processing_unit_type": "gpu"}  # type: Dict[str, str]
        else:
            self.gpu_training_param_dict = {"processing_unit_type": "cpu"}

        self.timeseries_param_dict = utilities._get_ts_params_dict(automl_settings)

        self.feature_skus = feature_skus_utilities.serialize_skus(
            feature_skus_utilities.get_feature_skus_from_settings(
                automl_settings
            )
        )

        self.verbosity = automl_settings.verbosity
        self.debug_log = automl_settings.debug_log


class ExperimentDataSettings:

    def __init__(self, automl_settings: AutoMLBaseSettings):
        self.validation_size = automl_settings.validation_size
        self.n_cross_validations = automl_settings.n_cross_validations
        self.y_min = automl_settings.y_min
        self.y_max = automl_settings.y_max
        self.num_classes = automl_settings.num_classes
        self.data_script = automl_settings.data_script
        self.label_column_name = automl_settings.label_column_name
        self.weight_column_name = automl_settings.weight_column_name
        self.cv_split_column_names = automl_settings.cv_split_column_names
        self.cv_step_size = getattr(automl_settings, "cv_step_size", None)


class ExperimentResourceSettings:

    def __init__(self, automl_settings: AutoMLBaseSettings):
        self.path = automl_settings.path
        self.max_cores_per_iteration = automl_settings.max_cores_per_iteration
        self.mem_in_mb = automl_settings.mem_in_mb
        self.enforce_time_on_windows = automl_settings.enforce_time_on_windows
        self.vm_type = automl_settings.vm_type
        self.environment_label = automl_settings.environment_label
