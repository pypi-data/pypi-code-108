# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""A container for information about the problem being worked on.

This is used to pass information to the server to use to give
better pipelines to try next.
"""
from typing import cast, Dict, List, Optional
import copy
import inspect
import json
import numpy as np

from azureml.automl.core import _codegen_utilities
from azureml.automl.runtime.shared import resource_limits
from azureml.automl.core.shared import constants
from azureml.automl.core.shared.constants import \
    TimeConstraintEnforcement as time_constraint


class ProblemInfo:
    """Container object for metadata about the problem being worked on.

    Provides more information that can be used to predict future pipelines
    This information is important for predicting the cost of a pipeline when
        the data is not directly available for inspection.
    """

    def __init__(
            self, dataset_samples=0, dataset_features=0, dataset_classes=0,
            dataset_num_categorical=0,
            dataset_categoricals=None,
            pipeline_categoricals=None,
            dataset_y_std=0,
            dataset_uid=None,
            runtime_constraints=None,
            num_threshold_buffers=3,
            num_recommendations=1,
            num_threads=1,
            is_sparse=False,
            pipeline_profile=constants.PipelineMaskProfiles.MASK_NONE,
            constraint_mode=time_constraint.TIME_CONSTRAINT_PER_ITERATION,
            cost_mode=constants.PipelineCost.COST_FILTER,
            task=constants.Tasks.CLASSIFICATION,
            training_percent=None,  # Default of None is 100%
            subsampling=False,
            metric="AUC_macro",
            model_names_whitelisted=None,
            model_names_blacklisted=None,
            kernel='linear',
            subsampling_treatment=constants.SubsamplingTreatment.LINEAR,
            subsampling_schedule=constants.SubsamplingSchedule.HYPERBAND_CLIP,
            cost_mode_param=None,
            iteration_timeout_mode=constants.IterationTimeout.TIMEOUT_NONE,
            iteration_timeout_param=None,
            feature_column_names=None,
            label_column_name=None,
            weight_column_name=None,
            cv_split_column_names=None,
            enable_streaming=None,
            timeseries_param_dict=None,
            gpu_training_param_dict=None,
            max_time=None):
        """Construct ProblemInfo.

        :param dataset_samples: number of samples in the whole dataset
        :param dataset_features: number of features in the dataset
        :param dataset_classes: number of classes in the targets of the dataset
        :param dataset_num_categorical: number of categorical features in
            the dataset
        :param dataset_categoricals: Boolean array indicating the categorical features
        :param dataset_y_std: standard deviation of targets
        :param dataset_uid: string identifier for dataset.
        :param runtime_constraints:
        :param num_threshold_buffers:
        :param num_recommendations:
        :param num_threads:
        :param is_sparse:
        :param pipeline_profile:
        :param constraint_mode:
        :param cost_mode: behavior to follow when filtering on costly pipelines
        :param task: machine learning task being executed
            (classification or regression)
        :param training_percent:
        :param subsampling: use subsampling
        :param metric: metric to be optimized
        :param model_names_whitelisted: model names to be whitelisted,
                the model names are in constants.LegacyModelNames, this take
                priority over blacklist models
        :param model_names_blacklisted: model names to be blacklisted,
                the model names are in constants.LegacyModelNames
        :param kernel: kernel to use for subsampling model
        :param subsampling_treatment: how to use subsampling percentage
        :param subsampling_schedule: how to schedule training percentages
        :param cost_mode_param: parameter that interacts with cost mode to select models
        :param iteration_timeout_mode: how to set and adjust iteration timeout
        :param iteration_timeout_param: parameter that interacts with timeout_mode to dynamically set timeouts
        :param feature_column_names: names of dataset feature columns
        :param label_column_name: name of dataset label column
        :param weight_column_name: name of dataset weight column
        :param cv_split_column_names: list of dataset cv split columns
        :param enable_streaming: whether to use streaming
        :param timeseries_param_dict: dict representing timeseries_params.
                See azureml.automl.core.shared.utilities._get_ts_params_dict for details.
        :param gpu_training_param_dict: dict representing gpu training related parameters.
        :param max_time: experiment timeout in seconds
        """
        self.dataset_samples = dataset_samples
        self.dataset_features = dataset_features
        self.dataset_classes = dataset_classes
        self.dataset_num_categorical = dataset_num_categorical
        self.dataset_categoricals = dataset_categoricals
        self.dataset_y_std = dataset_y_std
        self.dataset_uid = dataset_uid
        self.subsampling = subsampling
        self.task = task
        self.metric = metric
        self.num_threads = num_threads
        self.pipeline_profile = pipeline_profile
        self.is_sparse = is_sparse
        self.runtime_constraints = \
            runtime_constraints or resource_limits.DEFAULT_RESOURCE_LIMITS  # type: Dict[str, Optional[int]]
        self.constraint_mode = constraint_mode
        self.cost_mode = cost_mode
        self.training_percent = training_percent
        self.num_recommendations = num_recommendations
        self._server_threshold_events = 0
        self._num_threshold_buffers = num_threshold_buffers
        self._start_time = None
        self._current_time = None
        self.model_names_whitelisted = model_names_whitelisted
        self.model_names_blacklisted = model_names_blacklisted
        self._max_time = max_time
        self.kernel = kernel
        self.subsampling_treatment = subsampling_treatment
        self.subsampling_schedule = subsampling_schedule

        self.cost_mode_param = cost_mode_param
        self.iteration_timeout_mode = iteration_timeout_mode
        self.iteration_timeout_param = iteration_timeout_param

        self.feature_column_names = feature_column_names
        self.label_column_name = label_column_name
        self.weight_column_name = weight_column_name
        self.cv_split_column_names = cv_split_column_names
        self.enable_streaming = enable_streaming
        self.timeseries_param_dict = timeseries_param_dict
        self.gpu_training_param_dict = gpu_training_param_dict

        # Back compat for old SDK
        # The value itself is not used now, but old SDKs will expect the value to exist. On older SDKs, the
        # indices of the categorical columns will be injected as kwargs directly into the model, so the value here
        # is irrelevant.
        self.pipeline_categoricals = None

    def __repr__(self) -> str:
        params = self.__dict__.copy()
        default_values = ProblemInfo.get_default_parameters_and_values()
        new_params = {
            k: params[k] for k in params if not (k.startswith("_")
                                                 or k == 'runtime_constraints'
                                                 or (k in default_values
                                                 and np.all(default_values[k] == params[k])))
        }

        return _codegen_utilities.generate_repr_str(self.__class__, new_params)

    @classmethod
    def get_default_parameters_and_values(cls):
        """Inspect the params of the ProblemInfo constructor and return
        all the params that are assigned default values.
        """
        init_sig = inspect.signature(cls.__init__)
        default_param_values = {
            parameter: init_sig.parameters[parameter].default
            for parameter in init_sig.parameters
            if (
                init_sig.parameters[parameter].default != inspect.Parameter.empty
                and init_sig.parameters[parameter].kind
                in [
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.KEYWORD_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                ]
                and parameter != "self"
            )
        }

        return default_param_values

    @staticmethod
    def from_dict(d):
        """Create a ProblemInfo object.

        :param d: dictionary of dataset attributes
        :return: a ProblemInfo object
        """
        ret = ProblemInfo()
        ret.__dict__ = copy.deepcopy(d)
        return ret

    def to_dict(self):
        """Convert the current ProblemInfo object into a dictionary.

        :return: dictionary of dataset attributes
        """
        d = copy.deepcopy(self.__dict__)
        return d

    def __str__(self):
        """Get a string representation of the problem info."""
        return 'ProblemInfo(' + json.dumps(self.to_dict()) + ')'

    def get_time_constraint(self):
        """Get the time constraint placed on the experiment.

        :return: the time constraint
        """
        return self.runtime_constraints[resource_limits.TIME_CONSTRAINT]

    def set_time_constraint(self, new_constraint):
        """Set the time constraint placed on the experiment.

        :param new_constraint: int, time constraint in seconds
        """
        self.set_runtime_constraint({resource_limits.TIME_CONSTRAINT: new_constraint})

    def set_runtime_constraint(self, new_constraint):
        """
        Set the runtime constraint.

        :param new_constraint: a dict of constraints to be set.
            the keys for the constraints are in resource_limits.default_resource_limits
            if a constraint key does not exist in the dict it will be left unchanged.
        """
        if new_constraint:
            for c in resource_limits.DEFAULT_RESOURCE_LIMITS:
                if c in new_constraint:
                    self.runtime_constraints[c] = new_constraint[c]

    def handle_server_code(self, status_code):
        """Call on the client side to interpret server codes.

        :param status_code: A code sent from the server, e.g.
            to increase the time constraint.
        :param runner: The Runner object to also update if necessary.
        """
        if (self.constraint_mode
            == time_constraint.TIME_CONSTRAINT_PER_ITERATION
            and status_code and status_code
                == constants.ServerStatus.INCREASE_TIME_THRESHOLD):
            self._server_threshold_events += 1
            if self._server_threshold_events >= self._num_threshold_buffers:
                self._server_threshold_events = 0
                new_threshold = int(
                    cast(int, self.runtime_constraints[resource_limits.TIME_CONSTRAINT]) * 1.5)
                print('Increasing time constraint to {0}'.format(
                    new_threshold))
                self.runtime_constraints[
                    resource_limits.TIME_CONSTRAINT] = new_threshold

    def done(self, final_fit_expected_time=None):
        """Return true if client should halt training."""
        return (
            self.constraint_mode in [
                time_constraint.TIME_CONSTRAINT_TOTAL,
                time_constraint.TIME_CONSTRAINT_TOTAL_AND_ITERATION]
            and self.runtime_constraints[resource_limits.TOTAL_TIME_CONSTRAINT] <= (
                0 if final_fit_expected_time else final_fit_expected_time
            ))

    def set_start_time(self, t):
        """Set the start time."""
        self._start_time = t

    def update_time(self, t, training_times=0, predict_times=0):
        """Update the current time.

        :param t: current time measured by time.time()
        :param training_times: Optional parameter used when using cached results
            to account for the time we are skipping
        :param predict_times: Optional parameter to ignore the time that it takes
            to predict pipelines
        """
        self._current_time = t + training_times - predict_times
        if (self.constraint_mode in [
                time_constraint.TIME_CONSTRAINT_TOTAL,
                time_constraint.TIME_CONSTRAINT_TOTAL_AND_ITERATION]):
            self.runtime_constraints[resource_limits.TOTAL_TIME_CONSTRAINT] = int(
                self._max_time - (self._current_time - self._start_time))

    def set_cost_mode(self):
        """Set the cost mode for the problem."""
        if (self.dataset_samples is None or self.dataset_samples <= 0
            or self.dataset_classes is None or self.dataset_classes <= 0
            or self.dataset_features is None or self.dataset_features <= 0
            or self.get_time_constraint() is None
                or self.get_time_constraint() <= 0):
            self.cost_mode = constants.PipelineCost.COST_NONE

    def update_pipeline_profile(self, pipeline_profile):
        """
        Update the pipeline profile.

        Where the pipeline profile is the pipeline mask(s) to apply.
        """
        if isinstance(self.pipeline_profile, list):
            if (pipeline_profile not in
                    self.pipeline_profile):
                self.add_pipeline_profile(pipeline_profile)
        elif (self.pipeline_profile == constants.PipelineMaskProfiles.MASK_NONE
                or self.pipeline_profile is None):
            self.set_pipeline_profile(pipeline_profile)
        elif self.pipeline_profile != pipeline_profile:
            self.add_pipeline_profile(pipeline_profile)

    def add_pipeline_profile(self, pipeline_profile):
        """
        Add the pipeline profile.

        Where the pipeline profile is the pipeline mask(s) to apply.
        """
        if isinstance(self.pipeline_profile, list):
            self.pipeline_profile.append(pipeline_profile)
        else:
            self.pipeline_profile = [self.pipeline_profile, pipeline_profile]

    def set_pipeline_profile(self, pipeline_profile):
        """
        Set the pipeline profile.

        Where the pipeline profile is the pipeline mask(s) to apply.
        """
        self.pipeline_profile = pipeline_profile

    def clean_dataset_info(self):
        """Clean the ProblemInfo of all potentially sensitive user data."""
        self.dataset_categoricals = None

    def clean_attrs(self, useful_attrs: List[str]) -> 'ProblemInfo':
        "Clean ProblemInfo of all the unwanted attributes"
        params = self.__dict__.copy()
        default_values = ProblemInfo.get_default_parameters_and_values()
        for k in params:
            if (k in default_values
                and np.any(default_values[k] != params[k])
                and k != 'runtime_constraints'
                    and k not in useful_attrs):
                clean_params = {attr: params[attr] for attr in useful_attrs}
                return ProblemInfo(**clean_params)
        return self
