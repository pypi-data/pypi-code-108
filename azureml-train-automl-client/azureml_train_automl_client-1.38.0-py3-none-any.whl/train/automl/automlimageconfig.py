# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains configuration for submitting an automated ML image experiment in Azure Machine Learning.

This module inherits most of its functionality from AutoMLConfig and simplifies the interface for image tasks.
"""
import json
from typing import Any, Dict, List, Optional, Set, Union

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ImageDuplicateParameters, \
    ImageOddNumArguments, ImageParameterSpaceEmpty, InvalidArgumentType, InvalidArgumentWithSupportedValues, \
    MalformedArgument
from azureml.automl.core.shared.constants import ImageTask
from azureml.data import TabularDataset
from azureml.train.automl import AutoMLConfig, constants
from azureml.train.automl.exceptions import ValidationException
from azureml.train.hyperdrive import EarlyTerminationPolicy, HyperParameterSampling


class AutoMLImageConfig(AutoMLConfig):
    """
    Represents configuration for submitting an automated ML image experiment in Azure Machine Learning.

    This configuration object contains and persists the parameters for configuring the experiment run,
    as well as the training data to be used at run time. For guidance on selecting your
    settings, see: https://docs.microsoft.com/en-us/azure/machine-learning/how-to-auto-train-image-models.

    :param task: The type of task to run.
    :type task: ImageTask
    :param compute_target:
        The Azure Machine Learning compute target to run the ML image experiment on.
        Only remote GPU computes with more than 12 GB of GPU memory are supported.
        See https://docs.microsoft.com/azure/machine-learning/how-to-auto-train-remote for more
        information on compute targets.
    :type compute_target: Any
    :param training_data: The training data to be used within the experiment.
    :type training_data: TabularDataset
    :param hyperparameter_sampling:
        Object containing the hyperparameter space, the sampling method, and in some cases additional properties
        for specific sampling classes.
    :type hyperparameter_sampling: HyperParameterSampling
    :param iterations:
        The total number of different model and parameter combinations to test during an automated ML image
        experiment. If not specified, the default is 1 iteration.
    :type iterations: int
    :param max_concurrent_iterations:
        Represents the maximum number of iterations that would be executed in parallel. The default value
        is the same as the number of iterations provided.
    :type max_concurrent_iterations: Optional[int]
    :param experiment_timeout_hours:
        Maximum amount of time in hours that all iterations combined can take before the
        experiment terminates. Can be a decimal value like 0.25 representing 15 minutes. If not
        specified, the default experiment timeout is 6 days.
    :type experiment_timeout_hours: Optional[Union[float, int]]
    :param early_termination_policy:
        Early termination policy use when using hyperparameter tuning with several iterations.
        An iteration is cancelled when the criteria of a specified policy are met.
    :type early_termination_policy: Optional[EarlyTerminationPolicy]
    :param validation_data: The validation data to be used within the experiment.
    :type validation_data: Optional[TabularDataset]
    :param arguments:
        Arguments to be passed to the remote script runs. Arguments are passed in name-value pairs and the name
        must be prefixed by a double dash.
    :type arguments: Optional[List[Any]]
    """

    def __init__(self,
                 task: ImageTask,
                 compute_target: Any,
                 training_data: TabularDataset,
                 hyperparameter_sampling: HyperParameterSampling,
                 iterations: int,
                 max_concurrent_iterations: Optional[int] = None,
                 experiment_timeout_hours: Optional[Union[float, int]] = None,
                 early_termination_policy: Optional[EarlyTerminationPolicy] = None,
                 validation_data: Optional[TabularDataset] = None,
                 arguments: Optional[List[Any]] = None,
                 **kwargs: Any) -> None:
        """
        Create an AutoMLImageConfig.

        :param task: The type of task to run.
        :type task: ImageTask
        :param compute_target:
            The Azure Machine Learning compute target to run the ML image experiment on.
            Only remote GPU computes with more than 12 GB of GPU memory are supported.
            See https://docs.microsoft.com/azure/machine-learning/how-to-auto-train-remote for more
            information on compute targets.
        :type compute_target: Any
        :param training_data: The training data to be used within the experiment.
        :type training_data: TabularDataset
        :param hyperparameter_sampling:
            Object containing the hyperparameter space, the sampling method, and in some cases additional properties
            for specific sampling classes.
        :type hyperparameter_sampling: HyperParameterSampling
        :param iterations:
            The total number of different model and parameter combinations to test during an automated ML image
            experiment. If not specified, the default is 1 iteration.
        :type iterations: int
        :param max_concurrent_iterations:
            Represents the maximum number of iterations that would be executed in parallel. The default value
            is the same as the number of iterations provided.
        :type max_concurrent_iterations: Optional[int]
        :param experiment_timeout_hours:
            Maximum amount of time in hours that all iterations combined can take before the
            experiment terminates. Can be a decimal value like 0.25 representing 15 minutes. If not
            specified, the default experiment timeout is 6 days.
        :type experiment_timeout_hours: Optional[Union[float, int]]
        :param early_termination_policy:
            Early termination policy use when using hyperparameter tuning with several iterations.
            An iteration is cancelled when the criteria of a specified policy are met.
        :type early_termination_policy: Optional[EarlyTerminationPolicy]
        :param validation_data: The validation data to be used within the experiment.
        :type validation_data: Optional[TabularDataset]
        :param arguments:
            Arguments to be passed to the remote script runs. Arguments are passed in name-value pairs and the name
            must be prefixed by a double dash.
        :type arguments: Optional[List[Any]]
        """
        AutoMLImageConfig._validate_input_types(
            task=task, compute_target=compute_target, training_data=training_data,
            hyperparameter_sampling=hyperparameter_sampling, iterations=iterations,
            max_concurrent_iterations=max_concurrent_iterations, experiment_timeout_hours=experiment_timeout_hours,
            early_termination_policy=early_termination_policy, validation_data=validation_data, arguments=arguments)

        AutoMLImageConfig._validate_args_and_param_space(
            arguments=arguments, parameter_space=hyperparameter_sampling._parameter_space)

        experiment_timeout_hours = float(experiment_timeout_hours) if experiment_timeout_hours is not None else None

        # Initialize AutoMLConfig
        super().__init__(task=str(task.value),
                         compute_target=compute_target,
                         training_data=training_data,
                         validation_data=validation_data,
                         primary_metric=None,
                         experiment_timeout_hours=experiment_timeout_hours,
                         # Constant for image scenarios
                         enable_dnn=True,
                         featurization="off",
                         iterations=1,
                         max_concurrent_iterations=1,
                         # Kwargs
                         **kwargs)

        # Add additional image settings
        self.user_settings["hyperdrive_config"] = {
            "max_total_jobs": iterations,
            "max_concurrent_jobs": max_concurrent_iterations or iterations,
            "generator_config": {
                "name": hyperparameter_sampling._sampling_method_name,
                "parameter_space": json.dumps(hyperparameter_sampling._parameter_space),
                "properties": hyperparameter_sampling._properties
            },
            "policy_config": early_termination_policy.to_json() if early_termination_policy is not None else None
        }

        self.user_settings["arguments"] = arguments
        self.user_settings["run_source"] = constants.AUTOML_IMAGE_RUN_SOURCE

    @staticmethod
    def _validate_input_types(task: ImageTask, compute_target: Any, training_data: TabularDataset,
                              hyperparameter_sampling: HyperParameterSampling, iterations: int,
                              max_concurrent_iterations: Optional[int], experiment_timeout_hours: Optional[float],
                              early_termination_policy: Optional[EarlyTerminationPolicy],
                              validation_data: Optional[TabularDataset], arguments: Optional[List[Any]]) -> None:
        """
        Validate the types of the AutoMLImageConfig arguments.

        :param task: The type of task to run.
        :type task: ImageTask
        :param compute_target:
            The Azure Machine Learning compute target to run the ML image experiment on.
            Only remote GPU computes with more than 12 GB of GPU memory are supported.
            See https://docs.microsoft.com/azure/machine-learning/how-to-auto-train-remote for more
            information on compute targets.
        :type compute_target: Any
        :param training_data: The training data to be used within the experiment.
        :type training_data: TabularDataset
        :param hyperparameter_sampling:
            Object containing the hyperparameter space, the sampling method, and in some cases additional properties
            for specific sampling classes.
        :type hyperparameter_sampling: HyperParameterSampling
        :param iterations:
            The total number of different model and parameter combinations to test during an automated ML image
            experiment. If not specified, the default is 1 iteration.
        :type iterations: int
        :param max_concurrent_iterations:
            Represents the maximum number of iterations that would be executed in parallel. The default value
            is the same as the number of iterations provided.
        :type max_concurrent_iterations: Optional[int]
        :param experiment_timeout_hours:
            Maximum amount of time in hours that all iterations combined can take before the
            experiment terminates. Can be a decimal value like 0.25 representing 15 minutes. If not
            specified, the default experiment timeout is 6 days.
        :type experiment_timeout_hours: Optional[float]
        :param early_termination_policy:
            Early termination policy use when using hyperparameter tuning with several iterations.
            An iteration is cancelled when the criteria of a specified policy are met.
        :type early_termination_policy: Optional[EarlyTerminationPolicy]
        :param validation_data: The validation data to be used within the experiment.
        :type validation_data: Optional[TabularDataset]
        :param arguments:
            Arguments to be passed to the remote script runs. Arguments are passed in name-value pairs and the name
            must be prefixed by a double dash.
        :type arguments: Optional[List[Any]]
        """
        if not isinstance(task, ImageTask):
            raise ValidationException._with_error(
                AzureMLError.create(InvalidArgumentType, target="task", argument="task", actual_type=type(task),
                                    expected_types="ImageTask"))

        if compute_target is None:
            raise ValidationException._with_error(
                AzureMLError.create(ArgumentBlankOrEmpty, target="compute_target", argument_name="compute_target"))

        if not isinstance(training_data, TabularDataset):
            raise ValidationException._with_error(
                AzureMLError.create(InvalidArgumentType, target="training_data", argument="training_data",
                                    actual_type=type(training_data), expected_types="TabularDataset"))

        if not isinstance(hyperparameter_sampling, HyperParameterSampling):
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="hyperparameter_sampling", argument="hyperparameter_sampling",
                    actual_type=type(hyperparameter_sampling), expected_types="HyperParameterSampling"))

        if not isinstance(iterations, int):
            raise ValidationException._with_error(
                AzureMLError.create(InvalidArgumentType, target="iterations", argument="iterations",
                                    actual_type=type(iterations), expected_types="int"))

        if not isinstance(max_concurrent_iterations, (type(None), int)):
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="max_concurrent_iterations",
                    argument="max_concurrent_iterations", actual_type=type(max_concurrent_iterations),
                    expected_types=", ".join(["None", "int"])))

        if not isinstance(experiment_timeout_hours, (type(None), float, int)):
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="experiment_timeout_hours",
                    argument="experiment_timeout_hours", actual_type=type(experiment_timeout_hours),
                    expected_types=", ".join(["None", "float", "int"])))

        if not isinstance(early_termination_policy, (type(None), EarlyTerminationPolicy)):
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="early_termination_policy",
                    argument="early_termination_policy", actual_type=type(early_termination_policy),
                    expected_types=", ".join(["None", "EarlyTerminationPolicy"])))

        if not isinstance(validation_data, (type(None), TabularDataset)):
            raise ValidationException._with_error(
                AzureMLError.create(InvalidArgumentType, target="validation_data",
                                    argument="validation_data", actual_type=type(validation_data),
                                    expected_types=", ".join(["None", "TabularDataset"])))

        if not isinstance(arguments, (type(None), list)):
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="arguments",
                    argument="arguments", actual_type=type(arguments),
                    expected_types=", ".join(["None", "list"])))

    @ staticmethod
    def _validate_args_and_param_space(arguments: Optional[List[Any]], parameter_space: Dict[Any, Any]) -> None:
        """
        Validate arguments list and parameter space.

        :param arguments:
            Arguments to be passed to the remote script runs. Arguments are passed in name-value pairs and the name
            must be prefixed by a double dash.
        :type arguments: Optional[List[Any]]
        :param parameter_space: Dictionary containing parameters and their distributions
        :type parameter_space: Dict[Any, Any]
        """
        all_params = set()  # type: Set[str]

        AutoMLImageConfig._validate_args(arguments, all_params)
        AutoMLImageConfig._validate_param_space(parameter_space, all_params)

        if "model_name" not in all_params:
            AutoMLImageConfig._raise_model_name_missing_exception()

    @ staticmethod
    def _validate_args(arguments, all_params):
        """Validate arguments list."""
        if not arguments:
            return

        if len(arguments) % 2:
            raise ValidationException._with_error(
                AzureMLError.create(ImageOddNumArguments, target="arguments list", num_arguments=len(arguments)))

        # Iterate over keys
        for i in range(0, len(arguments), 2):

            # Check string type
            if not isinstance(arguments[i], str):
                AutoMLImageConfig._raise_non_string_parameter_name_exception(arguments[i])

            # Check it starts with "--"
            if not arguments[i].startswith("--"):
                raise ValidationException._with_error(
                    AzureMLError.create(
                        InvalidArgumentWithSupportedValues, target="argument key",
                        arguments="argument key", supported_values="--<argument name>"))

            key_without_prefix = arguments[i][2:]

            if key_without_prefix in all_params:
                AutoMLImageConfig._raise_duplicate_param_exception(key_without_prefix)

            all_params.add(key_without_prefix)

    @ staticmethod
    def _validate_param_space(param_space: Dict[str, Any], all_params: Set[str]) -> None:
        """Validate parameter space."""
        if not param_space:
            raise ValidationException._with_error(
                AzureMLError.create(ImageParameterSpaceEmpty, target="parameter space"))

        if not isinstance(param_space, dict):
            AutoMLImageConfig._raise_not_dict_param_space(param_space)

        # Iterate over keys
        for key in param_space:

            # Check string type
            if not isinstance(key, str):
                AutoMLImageConfig._raise_non_string_parameter_name_exception(key)

            # Check names don't start with "--"
            if key[:1] == "-" or key[:2] == "--":
                AutoMLImageConfig._raise_dash_prefix_in_params_exception()

            # Check value is not Boolean
            if isinstance(param_space[key], bool):
                AutoMLImageConfig._raise_boolean_value_exception(param_space[key])

            # Check choice value is not Boolean
            if isinstance(param_space[key], list) and param_space[key][0] == "choice":
                if isinstance(param_space[key][1][0][0], bool):
                    AutoMLImageConfig._raise_boolean_value_exception(param_space[key][1][0][0])

            if key in all_params:
                AutoMLImageConfig._raise_duplicate_param_exception(key)

            all_params.add(key)

        # Check conditional space after checking normal parameters
        if "model" in param_space:
            AutoMLImageConfig._check_conditional_subspaces(param_space["model"], all_params)

    @ staticmethod
    def _check_conditional_subspaces(conditional_space: List[Any], all_params: Set[Any]) -> None:
        """Validate conditional parameter subspaces."""
        if not isinstance(conditional_space, list):
            AutoMLImageConfig._raise_malformed_cond_subspace_exception()

        if not conditional_space or len(conditional_space) != 2:
            AutoMLImageConfig._raise_malformed_cond_subspace_exception()

        if conditional_space[0] != 'choice':
            AutoMLImageConfig._raise_malformed_cond_subspace_exception()

        subspaces = conditional_space[1][0]

        found_model_name = False

        for subspace in subspaces:
            if not isinstance(subspace, dict):
                AutoMLImageConfig._raise_not_dict_param_space(subspace)

            if not subspace:
                raise ValidationException._with_error(
                    AzureMLError.create(ImageParameterSpaceEmpty, target="conditional parameter subspace"))

            subspace_params = set()  # type: Set[str]

            for key in subspace:
                # Check string type
                if not isinstance(key, str):
                    AutoMLImageConfig._raise_non_string_parameter_name_exception(key)

                # Check names don't start with "--"
                if key[:1] == "-" or key[:2] == "--":
                    AutoMLImageConfig._raise_dash_prefix_in_params_exception()

                # Check value is not Boolean
                if isinstance(subspace[key], bool):
                    AutoMLImageConfig._raise_boolean_value_exception(subspace[key])

                # Check choice value is not Boolean
                if isinstance(subspace[key], list) and subspace[key][0] == "choice":
                    if isinstance(subspace[key][1][0][0], bool):
                        AutoMLImageConfig._raise_boolean_value_exception(subspace[key][1][0][0])

                if key in all_params or key in subspace_params:
                    AutoMLImageConfig._raise_duplicate_param_exception(key)

                subspace_params.add(key)

            if "model_name" not in all_params and "model_name" not in subspace_params:
                AutoMLImageConfig._raise_model_name_missing_exception()

            if "model_name" in subspace_params:
                found_model_name = True

        # Add model_name only after checking all subspaces
        if found_model_name:
            all_params.add("model_name")

    @ staticmethod
    def _raise_non_string_parameter_name_exception(parameter_name: Any) -> None:
        """Raise exception for non-string parameter name."""
        raise ValidationException._with_error(
            AzureMLError.create(
                InvalidArgumentType, target="parameter name",
                argument="parameter name", actual_type=type(parameter_name),
                expected_types="str"))

    @ staticmethod
    def _raise_duplicate_param_exception(parameter_name: str) -> None:
        """Raise exception for duplicate parameters."""
        raise ValidationException._with_error(
            AzureMLError.create(
                ImageDuplicateParameters, target="parameter name",
                parameter_name=parameter_name))

    @ staticmethod
    def _raise_boolean_value_exception(value: Any) -> None:
        """Raise exception for boolean argument value."""
        raise ValidationException._with_error(
            AzureMLError.create(
                InvalidArgumentType, target="parameter value",
                argument="parameter value", actual_type=type(value),
                expected_types="any type except boolean"))

    @ staticmethod
    def _raise_dash_prefix_in_params_exception() -> None:
        """Raise exception for dash prefix present in parameter."""
        raise ValidationException._with_error(
            AzureMLError.create(
                InvalidArgumentWithSupportedValues, target="parameter name",
                arguments="parameter name", supported_values="string without dash prefix"))

    @ staticmethod
    def _raise_model_name_missing_exception() -> None:
        """Raise exception for 'model_name' argument missing."""
        raise ValidationException._with_error(
            AzureMLError.create(
                InvalidArgumentWithSupportedValues, target="argument list or parameter space",
                arguments="argument list or parameter space",
                supported_values="must contain 'model_name'"))

    @ staticmethod
    def _raise_not_dict_param_space(param_space: Any) -> None:
        """Raise exception for non-dict parameter space."""
        raise ValidationException._with_error(
            AzureMLError.create(InvalidArgumentType, target="parameter space",
                                argument="parameter space", actual_type=type(param_space),
                                expected_types="dict"))

    @ staticmethod
    def _raise_malformed_cond_subspace_exception() -> None:
        """Raise exception for malformed conditional subspace."""
        raise ValidationException._with_error(
            AzureMLError.create(MalformedArgument, target="conditional parameter subspace",
                                argument_name="conditional parameter subspace"))
