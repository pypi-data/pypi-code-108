# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wrapper for pipeline fit output."""
import json
import traceback
from typing import Any, Dict, List, Optional, Set, Union, cast

from sklearn.pipeline import Pipeline as SKPipeline

import azureml.automl.core._exception_utilities as exception_utilities
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.shared import constants
from azureml.automl.core.shared import utilities
from azureml.automl.core.shared import utilities as common_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ExperimentTimedOut
from azureml.automl.core.shared.constants import TIMEOUT_TAG, MetricExtrasConstants
from azureml.automl.core.shared.exceptions import AutoMLException, ErrorTypes, PipelineRunException
from azureml.automl.core.shared.limit_function_call_exceptions import TimeoutException
from azureml.automl.runtime.shared.pipeline_spec import PipelineSpec
from azureml.core import Run

from .automl_pipeline import AutoMLPipeline
from .pipeline_run_helper import PipelineRunOutput


class FitOutput:
    """Data class encapsulating the return values from training."""

    MAX_OUTPUT_SIZE = 1024 * 1024

    def __init__(self,
                 primary_metric: str,
                 metric_operation: str,
                 num_classes: Optional[int],
                 pipeline: AutoMLPipeline) -> None:
        """
        Initialize a FitOutput object.

        :param pipeline: the pipeline being used to train
        """
        self._primary_metric = primary_metric
        self._metric_operation = metric_operation
        self._num_classes = num_classes
        self._errors = {}   # type: Dict[str, Dict[str, Union[BaseException, str, bool]]]
        self._pipeline = pipeline

        self._pipeline_run_output = None    # type: Optional[PipelineRunOutput]
        self._onnx_model = None
        self._onnx_model_resource = {}    # type: Dict[Any, Any]
        self._onnx_featurizer_model = None
        self._onnx_estimator_model = None

        self._hit_experiment_timeout = False

    def record_pipeline_results(self, pipeline_run_output: PipelineRunOutput) -> None:
        """
        Record the results from pipeline execution.

        :param pipeline_run_output: the pipeline execution return object
        """
        self._pipeline_run_output = pipeline_run_output

    def set_onnx_model(self, onnx_model: Any) -> None:
        """
        Set the onnx model of the fitted pipeline.

        :param onnx_model: the converted onnx model.
        """
        self._onnx_model = onnx_model

    def set_onnx_model_resource(self, onnx_model_res: Dict[Any, Any]) -> None:
        """
        Set the resource of onnx model.

        :param onnx_model_res: the resource of the converted onnx model.
        """
        self._onnx_model_resource = onnx_model_res

    def set_onnx_featurizer_model(self, onnx_featurizer_model: Any) -> None:
        """
        Set the featurizer onnx model of the fitted pipeline.

        :param onnx_model: the converted featurizer onnx model.
        """
        self._onnx_featurizer_model = onnx_featurizer_model

    def set_onnx_estimator_model(self, onnx_estimator_model: Any) -> None:
        """
        Set the estimator onnx model of the fitted pipeline.

        :param onnx_model: the converted estimator onnx model.
        """
        self._onnx_estimator_model = onnx_estimator_model

    @property
    def training_size(self) -> float:
        """Get the training size."""
        return self._pipeline.training_size

    @property
    def predicted_time(self) -> float:
        """Get the predicted time."""
        return self._pipeline.predicted_time

    @property
    def actual_time(self) -> float:
        """Get the actual time."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.fit_time
        else:
            return 0

    @property
    def fitted_pipeline(self) -> SKPipeline:
        """Get the fitted pipeline."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.fitted_pipeline
        else:
            return constants.Defaults.INVALID_PIPELINE_FITTED

    @property
    def fitted_pipelines_train(self) -> Union[SKPipeline, str]:
        """Get the partially trained fitted pipelines."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.fitted_pipelines_train
        else:
            return constants.Defaults.INVALID_PIPELINE_FITTED

    @property
    def onnx_model(self) -> Any:
        """Get the converted ONNX model."""
        return self._onnx_model

    @property
    def onnx_model_resource(self) -> Dict[Any, Any]:
        """Get the resource of the converted ONNX model."""
        return self._onnx_model_resource

    @property
    def onnx_featurizer_model(self) -> Any:
        """Get the converted ONNX featurizer model."""
        return self._onnx_featurizer_model

    @property
    def onnx_estimator_model(self) -> Any:
        """Get the converted ONNX estimator model."""
        return self._onnx_estimator_model

    @property
    def run_properties(self) -> Optional[str]:
        """Get the pipeline run properties."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.run_properties
        else:
            return None

    @property
    def run_preprocessor(self) -> Optional[str]:
        """Get the preprocessor name."""
        return self.pretrain_props['run_preprocessor']

    @property
    def run_algorithm(self) -> Optional[str]:
        """Get the algorithm name."""
        return self.pretrain_props['run_algorithm']

    @property
    def goal(self) -> str:
        """Get the training goal."""
        suffixes = {
            constants.OptimizerObjectives.MINIMIZE: 'min',
            constants.OptimizerObjectives.MAXIMIZE: 'max',
            constants.OptimizerObjectives.NA: 'NA'
        }
        suffix = suffixes.get(self._metric_operation)

        if suffix is None:
            raise NotImplementedError  # PII safe to raise directly

        return '{}_{}'.format(self._primary_metric, suffix)

    @property
    def pretrain_props(self) -> Dict[str, Optional[str]]:
        """Get the pretrain properties."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.pretrain_props
        else:
            return {
                'run_preprocessor': None,
                'run_algorithm': None
            }

    @property
    def primary_metric(self) -> str:
        """Get the primary metric."""
        return self._primary_metric

    @property
    def scores(self) -> Dict[str, Any]:
        """Get the pipeline scores."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.scores
        else:
            return constants.Defaults.INVALID_PIPELINE_VALIDATION_SCORES

    @property
    def score(self) -> float:
        """Get the primary pipeline score."""
        return self.scores.get(self.primary_metric, constants.Defaults.DEFAULT_PIPELINE_SCORE)

    @property
    def score_metric_extras(self) -> str:
        """Get the primary pipeline table metric in JSON format."""
        return json.dumps(self.scores.get(MetricExtrasConstants.MetricExtrasFormat.format(self.primary_metric),
                                          constants.Defaults.DEFAULT_PIPELINE_SCORE))

    @property
    def training_type(self) -> Optional[str]:
        """Get the training type."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.training_type
        else:
            return None

    @property
    def training_percent(self) -> int:
        """Get the training percent used for this pipeline"""
        return self._pipeline_run_output.training_percent if self._pipeline_run_output else 100

    @property
    def pipeline_script(self) -> str:
        """Get the pipeline script."""
        return self._pipeline.pipeline_script

    @property
    def pipeline_spec(self) -> Optional[PipelineSpec]:
        """Get the AutoML Pipeline Spec used in training."""
        if self._pipeline.pipeline_script:
            return PipelineSpec.from_dict(json.loads(self._pipeline.pipeline_script))

        return None

    @property
    def pipeline_id(self) -> str:
        """Get the pipeline hash id."""
        return self._pipeline.pipeline_id

    @property
    def num_classes(self) -> Optional[int]:
        """Get the number of classes for a classification task."""
        return self._num_classes

    @property
    def errors(self) -> Dict[str, Dict[str, Union[BaseException, str, bool]]]:
        """Get errors from training."""
        return self._errors

    @property
    def friendly_errors(self) -> str:
        """Get errors from training in JSON format."""
        return json.dumps(self._format_errors(self._errors))

    @property
    def failure_reason(self) -> Optional[str]:
        """Returns the *last* added exception's error type (i.e. UserError / System)"""
        if not self.errors:
            return None

        # TODO The behavior should be more explicit here - if there are multiple errors, only the last error type is
        # returned
        failure_reason = None   # type: Optional[str]
        for error_name in self.errors:
            if self.errors[error_name]['is_critical'] or failure_reason is None:
                exc = cast(BaseException, self.errors[error_name]['exception'])
                failure_reason = FitOutput._get_failure_reason_from_exception(exc)
        return failure_reason

    @property
    def error_code(self) -> Optional[str]:
        """Returns the *last* added exception's error code."""
        if not self.errors:
            return None

        # TODO The behavior should be more explicit here - if there are multiple errors, only the last error code is
        # returned
        error_code = None   # type: Optional[str]
        for error_name in self.errors:
            if self.errors[error_name]['is_critical'] or error_code is None:
                exc = cast(BaseException, self.errors[error_name]['exception'])
                error_code = FitOutput._get_error_code_from_exception(exc)
        return error_code

    def add_error(self, exception_type: str, exception: BaseException, is_critical: Optional[bool] = True) -> None:
        """Add an error to the list of training errors."""
        self._errors[exception_type] = {
            'exception': exception,
            'traceback': traceback.format_exc(),
            'is_critical': is_critical if is_critical else False,
            'has_pii': getattr(exception,
                               'has_pii', exception.has_pii if isinstance(exception, AutoMLException) else True)
        }

    def get_output_dict(self, exclude_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get a dictionary representing this object's output."""
        if exclude_keys is None:
            exclude_keys = []
        output = {
            'score': self.score,
            'score_table': self.score_metric_extras,
            'run_properties': self.run_properties,
            'pipeline_script': self.pipeline_script,
            'pipeline_id': self.pipeline_id,
            'training_type': self.training_type,
            'num_classes': self.num_classes,
            'predicted_time': self.predicted_time,
            'fit_time': self.actual_time,
            'goal': self.goal,
            'primary_metric': self.primary_metric,
            'errors': self.errors,
            'onnx_model': self.onnx_model,
            'onnx_model_resource': self.onnx_model_resource,
            'onnx_featurizer_model': self.onnx_featurizer_model,
            'onnx_estimator_model': self.onnx_estimator_model,
            self._primary_metric: self.score,
            'error_code': self.error_code,
            'failure_reason': self.failure_reason
        }
        output.update(self.pretrain_props)

        for key in exclude_keys:
            if key in output:
                del output[key]

        return output

    def get_sanitized_output_dict(self) -> Dict[str, Any]:
        """Get a dictionary representing this object's output with None values replaced with empty strings."""
        output_dict = self.get_output_dict()

        # Temporary hack to get around run property immutability.
        # TODO: Refactor pipeline_run_helper so we can get the pretrain properties inside fit_pipeline
        immutable_keys = [
            'run_preprocessor',
            'run_algorithm',
            'pipeline_spec',
            self._primary_metric
        ]
        # Exclude large objects from output.
        large_keys = [
            'onnx_model',
            'onnx_featurizer_model',
            'onnx_estimator_model'
        ]
        # Hide these keys from user.
        hidden_keys = [
            'predicted_time'
        ]
        for key in (immutable_keys + large_keys + hidden_keys):
            if key in output_dict:
                del output_dict[key]

        # Pre-convert the errors dictionary to JSON so that JOS can parse it (in particular, the has_pii flag)
        # Exception objects are not serializable, so they must be converted to string first
        if 'errors' in output_dict:
            new_error_dict = {}     # type: Dict[str, Any]
            for exception_type in output_dict['errors']:
                old_error_dict = output_dict['errors'][exception_type]
                # Attempt to convert the error to a log safe version of itself, so that it can be *always*
                # logged on the service side telemetry by JOS.
                sdk_error_dict = exception_utilities.to_log_safe_sdk_error(
                    exception=old_error_dict['exception'], error_name=exception_type
                )   # type: Dict[str, Any]
                if not sdk_error_dict:
                    # Fallback behavior, in case we could not get a log safe error. This is preserving the older
                    # behavior, so that the original error gets stored on the run DTO, and can be requested from
                    # the customer on-demand.
                    sdk_error_dict = {
                        exception_type: {
                            'exception': str(old_error_dict['exception']),
                            'traceback': old_error_dict['traceback'],
                            'is_critical': old_error_dict['is_critical'],
                            'has_pii': old_error_dict['has_pii']
                        }
                    }
                new_error_dict = {**new_error_dict, **sdk_error_dict}
            output_dict['errors'] = json.dumps(new_error_dict)

        output = utilities.convert_dict_values_to_str(output_dict)

        # Cap the output size to 1MB (the real limit is somewhat higher, but this is a good limit due to overhead)
        output_len = len(json.dumps(output))
        if output_len > FitOutput.MAX_OUTPUT_SIZE:
            raise PipelineRunException("Fit output size exceeded {} bytes, actual size is {} bytes."
                                       .format(FitOutput.MAX_OUTPUT_SIZE, output_len),
                                       target=PipelineRunException.PIPELINE_OUTPUT,
                                       has_pii=False)
        return output

    @staticmethod
    def _get_error_code_from_exception(exception: BaseException) -> str:
        error_code = common_utilities.get_error_code(exception)

        if error_code == ErrorTypes.Unclassified:
            return exception.__class__.__name__

        return error_code

    @staticmethod
    def _get_failure_reason_from_exception(exception: BaseException) -> str:
        error_code = common_utilities.get_error_code(exception, as_hierarchy=True)
        error_code_list = str.split(error_code, '.')

        # Error hierarchy is expected to be of the form 'UserError.X.Y' or 'System.X.Y' or 'Unclassified'
        return error_code_list[0]

    @staticmethod
    def _format_errors(errors: Dict[str, Any]) -> Dict[str, str]:
        friendly_errors = {}
        for error in errors:
            friendly_errors[error] = str(errors[error]['exception'])
        return friendly_errors


class _FitOutputUtils:

    @staticmethod
    @exception_utilities.service_exception_handler(raise_exception=False)
    def terminate_child_run(
            child_run: Run, fit_output: 'FitOutput', raise_exception: bool = False, is_aml_compute: bool = True
    ) -> None:
        """
        Sets the child run status to either 'Completed', 'Canceled' or 'Failed' depending on the errors contained
        within the provided fit_output.

        If there were any critical errors while fitting, the run is transitioned to a 'Failed' state, with the first
        critical error used as the error code. We cannot fail the run with multiple errors, all errors are currently
        stored as a property on the Run object.
        """
        all_errors = fit_output.errors

        # If an experiment times out, we cancel the currently executing child run
        timed_out = cast(Optional[Dict[str, BaseException]], all_errors.get(TIMEOUT_TAG))
        if timed_out is not None:
            timeout_exception = cast(TimeoutException, timed_out.get("exception"))
            if timeout_exception.error_code == ExperimentTimedOut().code:
                run_lifecycle_utilities.cancel_run(child_run, warning_string=timeout_exception.message)
                if raise_exception:
                    raise timeout_exception.with_traceback(timeout_exception.__traceback__)
                return

        # For any other critical errors, we fail the run with the corresponding exception
        for fit_exception in all_errors.values():
            if fit_exception.get("is_critical"):
                exception = cast(BaseException, fit_exception.get("exception"))
                run_lifecycle_utilities.fail_run(child_run, exception, is_aml_compute=is_aml_compute)
                if raise_exception:
                    raise exception.with_traceback(exception.__traceback__)
                return

        # Run completed normally
        run_lifecycle_utilities.complete_run(child_run)
