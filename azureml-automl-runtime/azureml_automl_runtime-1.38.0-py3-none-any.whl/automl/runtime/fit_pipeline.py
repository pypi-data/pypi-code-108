# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Code used to fit pipeline."""
import datetime
import json
import logging
import math
import uuid
from collections import defaultdict
from typing import Any, Dict, Optional, Tuple, cast

import numpy as np
import sklearn

from azureml._common._error_definition import AzureMLError
from azureml._tracing._tracer_factory import get_tracer
from azureml.automl.runtime.featurization_info_provider import FeaturizationInfoProvider

from azureml.exceptions import AzureMLException
from azureml.exceptions import ServiceException as AzureMLServiceException

import azureml.automl.core.inference as inference
from azureml.automl.core import package_utilities
from azureml.automl.core._run import RunType
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.model_explanation import ModelExpSupportStr
from azureml.automl.core.onnx_convert.onnx_convert_constants import OnnxConvertConstants
from azureml.automl.core.shared import constants, logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AutoMLInternal,
    ExperimentTimedOut,
    IterationTimedOut,
)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.constants import Transformers
from azureml.automl.core.shared.exceptions import (
    AutoMLException,
    ClientException,
    ErrorTypes,
    PipelineRunException,
    ServiceException,
)
from azureml.automl.core.shared.limit_function_call_exceptions import TimeoutException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.systemusage_telemetry import SystemResourceUsageTelemetry, SystemResourceUsageTelemetryFactory
from azureml.automl.runtime import _metrics_logging, cpu_utilities, pipeline_run_helper, training_utilities
from azureml.automl.runtime._runtime_params import (
    ExperimentControlSettings,
    ExperimentDataSettings,
    ExperimentOrchestrationSettings,
    ExperimentResourceSettings,
    PipelineSelectionSettings,
)
from azureml.automl.runtime.automl_run_context import AutoMLAbstractRunContext
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.shared.score import _scoring_utilities

from .automl_pipeline import AutoMLPipeline
from .data_context import TransformedDataContext
from .fit_output import FitOutput
from .onnx_convert import OnnxConverter

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


def fit_pipeline(
    automl_pipeline: AutoMLPipeline,
    control_settings: ExperimentControlSettings,
    resource_settings: ExperimentResourceSettings,
    orchestration_settings: ExperimentOrchestrationSettings,
    pipeline_selection_settings: PipelineSelectionSettings,
    data_settings: ExperimentDataSettings,
    automl_run_context: AutoMLAbstractRunContext,
    elapsed_time: Optional[int] = None,
    onnx_cvt: Optional[OnnxConverter] = None,
) -> FitOutput:
    """
    Run a single iteration of an AutoML experiment.

    This method is automatically called during a regular AutoML
    experiment. fit_pipeline will evaluate the pipeline for this iteration, fit the pipeline with the provided data,
    calculate the various metrics relevant for this experiment, and log all the results in the specified AzureML Run's
    history.

    :param automl_pipeline: AutoMLPipeline object containing pipeline id and serialized script.
    :param fit_pipeline_params: User settings for fitting this pipeline
    :param automl_run_context: child run context object
    :param elapsed_time: How long this experiment has already taken in minutes
    :param onnx_cvt: The onnx converter.
    :return: AzureML Run Properties for this child run
    """
    primary_metric = control_settings.primary_metric
    metric_operation = control_settings.metric_operation
    enable_streaming = control_settings.enable_streaming
    is_timeseries = control_settings.is_timeseries
    iteration_timeout_minutes = orchestration_settings.iteration_timeout_minutes
    experiment_timeout_minutes = orchestration_settings.experiment_timeout_minutes
    enable_onnx_compatible_models = pipeline_selection_settings.enable_onnx_compatible_models
    enable_split_onnx_featurizer_estimator_models = (
        pipeline_selection_settings.enable_split_onnx_featurizer_estimator_models
    )
    num_classes = data_settings.num_classes
    feature_skus = control_settings.feature_skus
    path = resource_settings.path
    save_mlflow = control_settings.save_mlflow
    log_binary = num_classes == 2 or control_settings.positive_label is not None

    logging_utilities.log_system_info(logger, prefix_message="[RunId:{}]".format(automl_run_context.run_id))

    start_time = datetime.datetime.now()

    telemetry_logger = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(interval=10)
    telemetry_logger.send_usage_telemetry_log(
        prefix_message="[RunId:{}][Starting fit_pipeline]".format(automl_run_context.run_id)
    )

    fit_output = FitOutput(primary_metric, metric_operation, num_classes, automl_pipeline)
    resource_tracker = cpu_utilities.ResourceUsageTracker()
    clamped = False

    try:
        with resource_tracker:
            # Check remaining time before pipeline run
            # If no time remaining, raises TimeoutException
            iteration_timeout_min, clamped = _check_iteration_time(
                iteration_timeout_minutes,
                experiment_timeout_minutes,
                constants.FitPipelineComponentName.PREPRARE_DATA,
                start_time,
                automl_pipeline.is_ensemble_pipeline,
                elapsed_time,
            )

            # Fit Pipeline
            _fit_pipeline_internal(
                automl_pipeline,
                automl_run_context,
                control_settings,
                resource_settings,
                fit_output,
                iteration_timeout_min,
                telemetry_logger,
            )

            with automl_run_context.get_run() as run:
                # Save model and log metrics
                _save_artifacts(
                    automl_run_context,
                    enable_streaming,
                    is_timeseries,
                    save_mlflow,
                    path,
                    fit_output,
                    control_settings.task_type,
                )

                if onnx_cvt and enable_onnx_compatible_models:
                    _convert_pipeline_to_onnx(
                        automl_pipeline,
                        automl_run_context,
                        enable_split_onnx_featurizer_estimator_models,
                        path,
                        run,
                        fit_output,
                        telemetry_logger,
                        onnx_cvt,
                    )

                # Log metric scores
                _metrics_logging.log_metrics(run, fit_output.scores, log_binary=log_binary)
                _metrics_logging.log_metrics_info(
                    fit_output.scores, pipeline_id=fit_output.pipeline_id, run_id=automl_run_context.run_id
                )
    except KeyboardInterrupt:
        logger.warning(
            "Received a KeyboardInterrupt, quitting execution for run {}.".format(automl_run_context.run_id)
        )
        raise
    except TimeoutException as e:
        fit_output._hit_experiment_timeout = clamped
        if clamped:
            # We hit timeout due to experiment timeout, fix the error code
            e = TimeoutException._with_error(
                AzureMLError.create(
                    ExperimentTimedOut,
                    target="parent_run",
                    reference_code=ReferenceCodes._FIT_PIPELINE_EXPERIMENT_TIMEOUT_CLAMPED_ITERATION_TIMEOUT,
                )
            )
        logger.error("Run {} terminated with error code {}.".format(automl_run_context.run_id, e.error_code))
        fit_output.add_error(constants.TIMEOUT_TAG, e)
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        # TODO: Bug #657527 fix nativeclient and local runs to handle is_critical
        #  and add exception to fit_output as non critical exception instead of logging
        if "is_critical" not in fit_output.errors.values():
            fit_output.add_error("overall", e)
    finally:
        _update_run_with_fit_output(automl_run_context, fit_output, resource_tracker, telemetry_logger, feature_skus)

    return fit_output


def _save_artifacts(
    automl_run_context: AutoMLAbstractRunContext,
    enable_streaming: bool,
    is_timeseries: bool,
    save_mlflow: bool,
    path: str,
    fit_output: FitOutput,
    task_type: str,
) -> None:
    """
    Stores any artifacts generated by the model training on the local file system (e.g. for Native Client runs)
    or uploads them to the artifact service (for regular local or remote runs).

    Pre-conditions: A successfully trained model
    Post-conditions: Artifacts registered (either locally or on user's storage account)

    An exception is raised if any errors are encountered while storing the artifacts, since that is considered a fatal
    error for the run.
    """
    with tracer.start_as_current_span(
        constants.TelemetryConstants.SPAN_FORMATTING.format(
            constants.TelemetryConstants.COMPONENT_NAME, constants.TelemetryConstants.METRIC_AND_SAVE_MODEL_NAME
        ),
        user_facing_name=constants.TelemetryConstants.METRIC_AND_SAVE_MODEL_USER_FACING,
    ):
        with logging_utilities.log_activity(
            logger,
            activity_name=constants.TelemetryConstants.METRIC_AND_SAVE_MODEL_NAME,
            custom_dimensions={"run_id": automl_run_context.run_id},
        ):
            try:
                _save_artifacts_internal(
                    fit_output, enable_streaming, is_timeseries, save_mlflow, automl_run_context, path, task_type
                )
            except (AutoMLException, AzureMLServiceException, AzureMLException):
                raise
            except Exception as e:
                logger.error("Failed to store artifacts, encountered an exception of type: {}".format(type(e)))
                ex = ClientException.from_exception(
                    e, target="SaveArtifact", reference_code=ReferenceCodes._FIT_PIPELINE_SAVE_ARTIFACT
                ).with_generic_msg("Failed to upload artifacts.")
                fit_output.add_error(constants.ARTIFACT_TAG, ex)
                raise ex


def _fit_pipeline_internal(
    automl_pipeline: AutoMLPipeline,
    automl_run_context: AutoMLAbstractRunContext,
    control_settings: ExperimentControlSettings,
    resource_settings: ExperimentResourceSettings,
    fit_output: FitOutput,
    iteration_timeout_min: Optional[int],
    telemetry_logger: SystemResourceUsageTelemetry,
) -> None:
    """Runs the given pipeline in a subprocess, recording any results in the provided fit_output."""
    try:
        with tracer.start_as_current_span(
            constants.TelemetryConstants.SPAN_FORMATTING.format(
                constants.TelemetryConstants.COMPONENT_NAME, constants.TelemetryConstants.RUN_TRAINING
            ),
            user_facing_name=constants.TelemetryConstants.RUN_TRAINING_USER_FACING,
        ):
            telemetry_logger.send_usage_telemetry_log(
                prefix_message="[RunId:{}][Before executing pipeline]".format(automl_run_context.run_id)
            )

            # Run Pipeline
            pipeline_run_output = pipeline_run_helper.run_pipeline(
                control_settings, resource_settings, automl_pipeline, automl_run_context, iteration_timeout_min
            )
            fit_output.record_pipeline_results(pipeline_run_output)

            # Check the result of pipeline run output.
            _check_fit_output_result(fit_output)

            logger.info("Pipeline execution finished with a score of {0}".format(fit_output.score))

            telemetry_logger.send_usage_telemetry_log(
                prefix_message="[RunId:{}][After executing pipeline]".format(automl_run_context.run_id)
            )
    except (AutoMLException, AzureMLServiceException, AzureMLException) as e:
        fit_output.add_error("fit", e)
        raise
    except Exception as e:
        fit_output.add_error("fit", e)
        raise PipelineRunException.from_exception(e).with_generic_msg(
            "Training child iteration failed for unexpected reason."
        )


def _convert_pipeline_to_onnx(
    automl_pipeline: AutoMLPipeline,
    automl_run_context: AutoMLAbstractRunContext,
    enable_split_onnx_featurizer_estimator_models: bool,
    path: str,
    run: RunType,
    fit_output: FitOutput,
    telemetry_logger: SystemResourceUsageTelemetry,
    onnx_cvt: OnnxConverter,
) -> None:
    """Convert the given pipeline to an ONNX compatible one."""
    try:
        from azureml.core import Run

        with tracer.start_as_current_span(
            constants.TelemetryConstants.SPAN_FORMATTING.format(
                constants.TelemetryConstants.COMPONENT_NAME, constants.TelemetryConstants.ONNX_CONVERSION
            ),
            user_facing_name=constants.TelemetryConstants.ONNX_CONVERSION_USER_FACING,
        ):
            with logging_utilities.log_activity(
                logger,
                activity_name=constants.TelemetryConstants.ONNX_CONVERSION,
                custom_dimensions={"run_id": automl_run_context.run_id},
            ):
                # Convert to ONNX if user indicates using ONNX compatible models,
                # after we got this valid fitted_pipeline.
                # Inject the exp name, run id data into the onnx model.
                onnx_mdl_name = "AutoML_ONNX_Model_[{}]".format(run.id)
                exp_name = ""
                # Experiment name will remain empty for native client runs
                if (
                    isinstance(run, Run)
                    and hasattr(run, "experiment")
                    and run.experiment is not None
                    and hasattr(run.experiment, "name")
                ):
                    exp_name = run.experiment.name
                onnx_mdl_desc = {
                    "AutoMLSDKVer": onnx_cvt.producer_version,
                    "ExperimentName": exp_name,
                    "RunId": run.id,
                    "PipeId": automl_pipeline.pipeline_id,
                }
                telemetry_logger.send_usage_telemetry_log(
                    prefix_message="[RunId:{}][Start ONNX Convert in fit pipeline]".format(automl_run_context.run_id)
                )
                onnx_model, featurizer_onnx_model, estimator_onnx_model, _ = onnx_cvt.convert(
                    raw_model=fit_output.fitted_pipeline, model_name=onnx_mdl_name, model_desc=onnx_mdl_desc
                )
                telemetry_logger.send_usage_telemetry_log(
                    prefix_message="[RunId:{}][End ONNX Convert in fit pipeline]".format(automl_run_context.run_id)
                )
                # If the converted onnx model is valid, save the ONNX model.
                if onnx_model is not None:
                    automl_run_context.save_onnx_model_output(onnx_model, constants.MODEL_PATH_ONNX, path)
                    fit_output.set_onnx_model(onnx_model)
                    onnx_resource = onnx_cvt.get_converted_onnx_model_resource()
                    fit_output.set_onnx_model_resource(onnx_resource)
                    if onnx_resource:
                        automl_run_context.save_onnx_model_resource(
                            onnx_resource, constants.MODEL_RESOURCE_PATH_ONNX, path
                        )
                if enable_split_onnx_featurizer_estimator_models:
                    # Save the splited onnx models.
                    if featurizer_onnx_model is not None:
                        automl_run_context.save_onnx_model_output(
                            featurizer_onnx_model, OnnxConvertConstants.FeaturizerOnnxModelPath, path
                        )
                        fit_output.set_onnx_featurizer_model(featurizer_onnx_model)
                    if estimator_onnx_model is not None:
                        automl_run_context.save_onnx_model_output(
                            estimator_onnx_model, OnnxConvertConstants.EstimatorOnnxModelPath, path
                        )
                        fit_output.set_onnx_estimator_model(estimator_onnx_model)
    except Exception as e:
        fit_output.add_error("ONNX_CONVERSION", e, is_critical=False)
        logging_utilities.log_traceback(e, logger, is_critical=False)
        logger.warning("[RunId:{}]Failed ONNX Conversion in fit pipeline.".format(run.id))


def _update_run_with_fit_output(
    automl_run_context: AutoMLAbstractRunContext,
    fit_output: FitOutput,
    resource_tracker: cpu_utilities.ResourceUsageTracker,
    telemetry_logger: SystemResourceUsageTelemetry,
    feature_skus: str,
) -> None:
    # TODO: remove once backend can handle nulls
    fit_output_sanitized = fit_output.get_sanitized_output_dict()
    with automl_run_context.get_run() as run:
        # Check to see if any property already exists, and exclude if already present
        fit_output_sanitized.update({"dependencies_versions": json.dumps(package_utilities.get_sdk_dependencies())})

        # Add v2 metrics to properties
        fit_output_sanitized.update(
            {
                "num_cores": cpu_utilities.get_cpu_core_count(),
                "num_logical_cores": cpu_utilities.get_cpu_core_count(True),
                "peak_memory_usage": resource_tracker.peak_mem_usage,
                "vm_configuration": cpu_utilities.get_cpu_name(),
                "core_hours": resource_tracker.total_cpu_time / 3600,
                "feature_skus": feature_skus,
            }
        )

        existing_properties = run.get_properties()
        run.add_properties(
            # remove empty value
            {
                k: str(v)
                for k, v in fit_output_sanitized.items()
                if k not in existing_properties and v is not None and str(v)
            }
        )

    telemetry_logger.send_usage_telemetry_log(
        prefix_message="[RunId:{}][End fit_pipeline]".format(automl_run_context.run_id)
    )
    telemetry_logger.stop()


def _save_artifacts_internal(
    fit_output: FitOutput,
    enable_streaming: bool,
    is_timeseries: bool,
    save_mlflow: bool,
    automl_run_context: AutoMLAbstractRunContext,
    working_dir: str,
    task_type: str,
) -> None:
    # Container for location of files to be saved in the artifact store
    models_to_save = _get_fitted_models_path_dict(fit_output)
    artifacts_to_save = _create_artifact_strings(fit_output, task_type, is_timeseries, enable_streaming)

    with automl_run_context.get_run() as run:
        try:
            automl_run_context.batch_save_artifacts(
                working_dir,
                artifacts_to_save,
                models_to_save,
                save_mlflow)
        except (AutoMLException, AzureMLServiceException) as e:
            logging_utilities.log_traceback(e, logger)
            logger.error("Encountered an error on the service while uploading artifacts to the run.")
            fit_output.add_error(constants.ARTIFACT_TAG, e)
            raise
        except Exception as e:
            if isinstance(e, AzureMLException):
                error_code, error_type, target = logging_utilities._get_error_details(e, logger)
                if error_code != ErrorTypes.Unclassified:
                    raise
            ex = ServiceException.from_exception(
                e, target="SaveArtifact", reference_code=ReferenceCodes._FIT_PIPELINE_ARTIFACT_BATCH_SAVE
            ).with_generic_msg("Failed to batch save artifacts")
            logging_utilities.log_traceback(e, logger)
            logger.error(
                "Encountered an error while uploading artifacts to the run. Exception type: {}".format(
                    e.__class__.__name__
                )
            )
            fit_output.add_error(constants.ARTIFACT_TAG, ex)
            raise ex

        # Save artifact ids as run properties
        properties_to_add = automl_run_context._get_artifact_id_run_properties()
        properties_to_add.update(
            {
                ModelExpSupportStr: str(training_utilities._get_model_exp_property(run)),
                inference.AutoMLInferenceArtifactIDs.PipelineGraphVersion: constants.PIPELINE_GRAPH_VERSION,
            }
        )
        model_name = inference._get_model_name(run.id)
        if model_name:
            properties_to_add[inference.AutoMLInferenceArtifactIDs.ModelName] = model_name
        logger.info(
            "Updating child run properties with model name {} and size {} bytes.".format(
                model_name, properties_to_add[inference.AutoMLInferenceArtifactIDs.ModelSizeOnDisk]
            )
        )
        run.add_properties(properties_to_add)


def _create_artifact_strings(
        fit_output: FitOutput, task_type: str, is_timeseries: bool, enable_streaming: bool
) -> Dict[str, str]:
    """
    Get a dictionary of artifacts to save for the trial.
    Key is the file path to save to, value are the file contents as string.
    """
    env_artifacts = _get_env_dep_path_dict(fit_output)
    scoring_artifacts = _get_scoring_files_path_dict(fit_output, enable_streaming, is_timeseries, task_type)
    viz_artifacts = _get_pipeline_viz_path_dict(fit_output, enable_streaming)
    featurization_artifacts = _get_featurization_info_path_dict(fit_output)
    all_artifacts = {**env_artifacts, **scoring_artifacts, **viz_artifacts, **featurization_artifacts}
    return all_artifacts


def _get_pipeline_viz_path_dict(fit_output: FitOutput, enable_streaming: bool) -> Dict[str, str]:
    """
    Return a dictionary mapping the path where the pipeline visualization graph file is saved.
    The graph can also be an empty dict.
    """
    viz_files_to_save = {}  # type: Dict[str, Any]
    try:
        # Visualization for streaming is currently not supported
        if not enable_streaming:
            graph_json_dict = _transform_graph(fit_output.fitted_pipeline)  # type: Any
            viz_files_to_save[constants.PIPELINE_GRAPH_PATH] = json.dumps(graph_json_dict, indent=4)
    except Exception as e:
        ex = ClientException.from_exception(
            e, target="SaveArtifact", reference_code=ReferenceCodes._FIT_PIPELINE_TRANSFORM_PIPELINE_GRAPH
        ).with_generic_msg("Failed to transform graph and get pipeline graph file.")
        fit_output.add_error(constants.ARTIFACT_TAG, ex)
        raise ex
    return viz_files_to_save


def _get_scoring_files_path_dict(
        fit_output: FitOutput, enable_streaming: bool, is_timeseries: bool, task_type: str
) -> Dict[str, str]:
    """Return a dictionary of the paths to which the scoring files are saved"""
    scoring_files_to_save = {}  # type: Dict[str, Any]
    # Add scoring file path and get model name to save
    expr_store = ExperimentStore.get_instance()
    if expr_store.metadata.raw_data_type is None and not enable_streaming:
        ex = ClientException(
            "Failed to get scoring file: dataset's raw_data_type is not set.",
            has_pii=False,
            target="SaveArtifact",
            reference_code=ReferenceCodes._FIT_PIPELINE_DATASET_GET_RAW_DATA_TYPE,
        )
        fit_output.add_error(constants.ARTIFACT_TAG, ex)
        raise ex
    try:
        # Models trained with streaming (i.e. Dataflow) can only infer on a pandas Dataframe
        if_pandas_type = (enable_streaming or expr_store.metadata.raw_data_type == inference.PandasParameterType)
        scoring_file_str_v1, scoring_file_str_v2 = inference._get_scoring_file(
            is_pandas_data_frame=if_pandas_type,
            input_sample_str=expr_store.metadata.raw_data_snapshot_str,
            output_sample_str=expr_store.metadata.output_snapshot_str,
            is_forecasting=is_timeseries,
            task_type=task_type
        )
        scoring_files_to_save[constants.SCORING_FILE_PATH] = scoring_file_str_v1
        scoring_files_to_save[constants.SCORING_FILE_V2_PATH] = scoring_file_str_v2
    except Exception as e:
        ex = ClientException.from_exception(
            e, target="SaveArtifact", reference_code=ReferenceCodes._FIT_PIPELINE_GET_SCORING_FILE
        ).with_generic_msg("Failed to get scoring file.")
        fit_output.add_error(constants.ARTIFACT_TAG, ex)
        raise ex

    return scoring_files_to_save


def _get_env_dep_path_dict(fit_output: FitOutput) -> Dict[str, str]:
    """Generate a Conda Environment dependency file, and return the path to which to persist it to"""
    env_files_to_save = {}  # type: Dict[str, Any]
    all_dependencies = package_utilities._all_dependencies()
    # TODO Change to log only azureml packages
    # logger.info("All versions str:\n{}".format(json.dumps(all_dependencies)))
    env_files_to_save[constants.DEPENDENCIES_PATH] = json.dumps(all_dependencies, indent=4)
    # add conda environment file path
    is_text_dnn = hasattr(fit_output.fitted_pipeline, "steps") and any(
        [getattr(step[1], "_is_text_dnn", False) for step in fit_output.fitted_pipeline.steps]
    )
    try:
        env_files_to_save[constants.CONDA_ENV_FILE_PATH] = inference._create_conda_env_file(
            include_dnn_packages=is_text_dnn
        )
    except ImportError:
        # ModuleNotFoundError not exist in all python versions
        logger.warning("Skipping to create conda env file for native client. ")
    except Exception as e:
        ex = ClientException.from_exception(
            e, target="SaveArtifact", reference_code=ReferenceCodes._FIT_PIPELINE_CREATE_CONDA_ENV_FILE
        ).with_generic_msg("Failed to get scoring file.")
        fit_output.add_error(constants.ARTIFACT_TAG, ex)
        raise ex

    return env_files_to_save


def _get_fitted_models_path_dict(fit_output: FitOutput) -> Dict[str, Any]:
    """Returns a dictionary with key being the path where the value (the model) needs to be saved"""
    models_to_save = {constants.MODEL_PATH: fit_output.fitted_pipeline}
    # Save CV trained models. This is done to increase transparency of AutoML training as some customers
    # have started looking at the CV models. It is also done as an optimization for ensembling.
    # We persist the partially trained fitted models as they will be used for computing the scores
    # during ensemble hill climbing.
    if fit_output.fitted_pipelines_train != constants.Defaults.INVALID_PIPELINE_OBJECT:
        logger.info("Saving the partially trained fitted models.")
        models_to_save[constants.MODEL_PATH_TRAIN] = fit_output.fitted_pipelines_train
    return models_to_save


def _get_featurization_info_path_dict(fit_output: FitOutput) -> Dict[str, str]:
    """Return a dictionary of the paths to which the featurization information should be saved"""
    feat_files_to_save = {}  # type: Dict[str, Any]

    preprocessor = fit_output.fitted_pipeline.steps[0][1]   # type: FeaturizationInfoProvider
    if not isinstance(preprocessor, FeaturizationInfoProvider):
        # Featurization wasn't available for this trial, don't need to save anything
        return feat_files_to_save

    engg_feat_names = preprocessor.get_engineered_feature_names()
    feat_summary = preprocessor.get_featurization_summary(is_user_friendly=False)

    feat_files_to_save[constants.FEATURIZATION_ENGG_FEAT_NAMES_PATH] = json.dumps(engg_feat_names)
    feat_files_to_save[constants.FEATURIZATION_SUMMARY_PATH] = json.dumps(feat_summary)

    return feat_files_to_save


def _extract_data(
    fit_iteration_parameters_dict: Optional[Dict[str, Any]] = None,
    transformed_data_context: Optional[TransformedDataContext] = None,
) -> Tuple[Any, Any, Any, Any, Any, Any, Any, Any]:
    # if transformed_data_context is not None, then use data in transformed_data_context. If None, then to
    # use data in fit_iteration_parameters_dict.
    if transformed_data_context is not None:
        X = transformed_data_context.X
        y = transformed_data_context.y
        X_valid = transformed_data_context.X_valid
        y_valid = transformed_data_context.y_valid
        sample_weight = transformed_data_context.sample_weight
        sample_weight_valid = transformed_data_context.sample_weight_valid
        cv_splits_indices = transformed_data_context.cv_splits_indices
        x_raw_column_names = transformed_data_context.x_raw_column_names
    elif fit_iteration_parameters_dict is not None:
        X = fit_iteration_parameters_dict.get("X")
        y = fit_iteration_parameters_dict.get("y")
        X_valid = fit_iteration_parameters_dict.get("X_valid")
        y_valid = fit_iteration_parameters_dict.get("y_valid")
        sample_weight = fit_iteration_parameters_dict.get("sample_weight")
        sample_weight_valid = fit_iteration_parameters_dict.get("sample_weight_valid")
        cv_splits_indices = fit_iteration_parameters_dict.get("cv_splits_indices")
        x_raw_column_names = fit_iteration_parameters_dict.get("x_raw_column_names")
    else:
        raise PipelineRunException(
            "Either a transformed data context or parameters dict is required to extract data.",
            target=PipelineRunException.PIPELINE_RUN_REQUIREMENTS,
            has_pii=False,
        )
    return X, y, X_valid, y_valid, sample_weight, sample_weight_valid, cv_splits_indices, x_raw_column_names


# helper function to create edges
def edge_helper(
    source_node_id: Optional[str],
    source_node_name: Optional[str],
    source_name: Optional[str],
    target_name: Optional[str],
    dst_node_id: Optional[str],
    dst_node_name: Optional[str],
    graph_json_dict: Dict[str, Any],
) -> None:
    edge = {}  # type: Dict[str, Any]
    edge["source_node_id"] = source_node_id
    edge["source_node_name"] = source_node_name
    edge["source_name"] = source_name
    edge["target_name"] = target_name
    edge["dst_node_id"] = dst_node_id
    edge["dst_node_name"] = dst_node_name
    graph_json_dict["edges"].append(edge)


def _transform_graph(fitted_model: sklearn.pipeline.Pipeline) -> Any:
    feature_summary_dict = defaultdict()  # type: Any

    # check preprocess is set to True by the user
    is_preprocess = False
    for step in fitted_model.steps:
        if step[0] == Transformers.X_TRANSFORMER or step[0] == Transformers.TIMESERIES_TRANSFORMER:
            is_preprocess = True
            break
    if not is_preprocess:
        # TODO returned the datasource node
        # along with the fitted_pipeline nodes (scaler + final estimator)
        return {}

    model_lst = []
    # append schema_name and version to differenciate different json files in the future
    # initialize the keys
    complete_graph_json_dict = defaultdict()  # type: Any
    complete_graph_json_dict["schema_name"] = "pipeline_graph"
    complete_graph_json_dict["schema_version"] = "1.0.0"
    graph_json_dict = defaultdict()  # type: Any
    graph_json_dict["module_nodes"] = {}
    graph_json_dict["edges"] = []
    graph_json_dict["child_runs"] = []

    for step in fitted_model.steps:
        if step[0] == Transformers.X_TRANSFORMER or step[0] == Transformers.TIMESERIES_TRANSFORMER:
            total_col = 0
            for summary in step[1].get_featurization_summary():
                total_col += 1
                feature_count = str(summary["EngineeredFeatureCount"])
                if summary["TypeDetected"] in feature_summary_dict:
                    tf = " ".join(summary["Transformations"])
                    feature_summary_dict[summary["TypeDetected"]][tf].append(summary["RawFeatureName"])
                    feature_summary_dict[summary["TypeDetected"]]["EngineeredFeatureCount"] = [feature_count]
                else:
                    transformation_col_dict = defaultdict(list)  # type: Any
                    tf = " ".join(summary["Transformations"])
                    transformation_col_dict[tf].append(summary["RawFeatureName"])
                    transformation_col_dict["EngineeredFeatureCount"] = [feature_count]
                    feature_summary_dict[summary["TypeDetected"]] = transformation_col_dict

        else:
            md_id = uuid.uuid4().hex[:8]
            model = {"node_id": md_id, "model_name": step[0]}
            graph_json_dict["module_nodes"][md_id] = {"node_id": md_id, "name": step[0], "status": "model"}
            model_lst.append(model)

    name = "data_source - " + str(total_col) + " col"
    src_id = uuid.uuid4().hex[:8]
    graph_json_dict["datasource_nodes"] = {src_id: {"node_id": src_id, "name": name}}

    # Each run will have a graph_json_dict that contains the information of data_source_nodes,
    # module_nodes, edges

    for i in range(len(model_lst) - 1):
        edge_helper(model_lst[i]["node_id"], "", "", "", model_lst[i + 1]["node_id"], "", graph_json_dict)

    for i, data_type in enumerate(feature_summary_dict):
        ds_id = uuid.uuid4().hex[:8]
        graph_json_dict["module_nodes"][ds_id] = {"node_id": ds_id, "name": data_type, "status": "dataType"}
        # connect the data source to all the data types, display incoming col number and outgoing col number
        # calculate number of cols that go into every data type
        num_col_per_type = 0
        for key, val in feature_summary_dict[data_type].items():
            if key != "EngineeredFeatureCount":
                num_col_per_type += len(val)
        target_name = str(num_col_per_type) + " col"
        edge_helper(src_id, "data_source", "", target_name, ds_id, data_type, graph_json_dict)
        # connect each operation with the model, data type and chain up the models
        for key, val in feature_summary_dict[data_type].items():
            operation_id_lst = []
            if key != "" and key != "EngineeredFeatureCount":
                operation_lst = key.split()
                for j, op in enumerate(operation_lst):
                    op_id = uuid.uuid4().hex[:8]
                    operation_dict = {"node_id": op_id, "op_name": op}
                    operation_id_lst.append(operation_dict)
                    graph_json_dict["module_nodes"][op_id] = {"node_id": op_id, "name": op, "status": "operation"}
                    # chain up the operation
                    # first operation, connect with feature_summary_dict type nodes
                    if j == 0:
                        edge_helper(ds_id, "", "", "", op_id, "", graph_json_dict)
                    # last operation connect with model node
                    if j == len(operation_lst) - 1:
                        if len(model_lst) > 0:
                            output_name = feature_summary_dict[data_type]["EngineeredFeatureCount"][0] + " col"
                            edge_helper(op_id, "", "", output_name, model_lst[0]["node_id"], "", graph_json_dict)
                    # inbetween operations
                    if j > 0:
                        edge_helper(operation_id_lst[j - 1]["node_id"], "", "", "", op_id, "", graph_json_dict)

    complete_graph_json_dict["data"] = graph_json_dict
    return complete_graph_json_dict


def _check_iteration_time(
    iteration_timeout_min: Optional[int],
    experiment_timeout_min: Optional[int],
    component_name: str,
    start_time: datetime.datetime,
    is_ensemble_pipeline: bool = False,
    elapsed_time: Optional[int] = None,
    raise_exception: Optional[bool] = True,
) -> Tuple[Optional[int], bool]:
    # Check Time Spent So Far for the Component
    running_min = (datetime.datetime.now() - start_time).total_seconds() / 60.0
    logger.info("Component {} finished after {} minutes.".format(component_name, running_min))

    clamped = False

    # Check Iteration Time
    if iteration_timeout_min is not None:
        iteration_timeout_min = math.ceil(iteration_timeout_min - running_min)
        if iteration_timeout_min <= 0 and raise_exception:
            logger.warning("Iteration ran for {} minutes. Terminating child run.".format(math.floor(running_min)))
            raise TimeoutException._with_error(
                AzureMLError.create(
                    IterationTimedOut,
                    target="child_run",
                    reference_code=ReferenceCodes._FIT_PIPELINE_ITERATION_TIMEOUT,
                )
            )

    # Check Experiment Time
    # If experiment is already over and in Voting/Stack Ensemble, then skip this check
    if not is_ensemble_pipeline:
        if experiment_timeout_min is not None and elapsed_time is not None:
            remaining_experiment_min = math.ceil(int(experiment_timeout_min) - elapsed_time - running_min)
            if remaining_experiment_min <= 0 and raise_exception:
                logger.warning(
                    "Experiment ran for {} minutes. Terminating parent run.".format(
                        math.floor(elapsed_time + running_min)
                    )
                )
                raise TimeoutException._with_error(
                    AzureMLError.create(
                        ExperimentTimedOut,
                        target="parent_run",
                        reference_code=ReferenceCodes._FIT_PIPELINE_EXPERIMENT_TIMEOUT,
                    )
                )
            # Update iteration timeout if remaining experiment min is smaller
            if iteration_timeout_min is None or remaining_experiment_min < iteration_timeout_min:
                iteration_timeout_min = remaining_experiment_min
                clamped = True

    return iteration_timeout_min, clamped


def _check_fit_output_result(fit_output: FitOutput) -> None:
    """Check the run results."""
    if fit_output.score in [None, np.nan, constants.Defaults.DEFAULT_PIPELINE_SCORE]:
        message = "An unexpected error occurred when getting the {} score.".format(fit_output.primary_metric)
        raise PipelineRunException._with_error(
            AzureMLError.create(
                AutoMLInternal,
                target=PipelineRunException.PIPELINE_OUTPUT,
                reference_code=ReferenceCodes._FIT_PIPELINE_GET_SCORE,
                error_details=message,
            )
        )

    if fit_output.fitted_pipeline == constants.Defaults.INVALID_PIPELINE_OBJECT:
        raise PipelineRunException(
            "Fitted model is empty.", target=PipelineRunException.PIPELINE_OUTPUT, has_pii=False
        )
