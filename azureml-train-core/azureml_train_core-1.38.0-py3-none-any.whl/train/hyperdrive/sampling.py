# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The hyperparameter sampling definitions."""
import inspect
import sys
from abc import ABC

from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore
from azureml.train.hyperdrive.error_definition import (
    DictValidationInvalidArgument, DistributionValidationFailure,
    InvalidConfigSetting, InvalidKeyInDict, InvalidType,
    RehydrateUnknownSampling)
from azureml.train.hyperdrive.exceptions import (HyperDriveConfigException,
                                                 HyperDriveRehydrateException)

scrubbed_data = "[Scrubbed]"


def _sampling_from_dict(dict_sampling):
    """Construct a Sampling object from a dictionary.

    The dictionary is supposed to come from a previous run that's retrieved from the cloud.
    This is an internal utility method.

    :param dict_sampling: A dictionary of the sampling.
    :type dict_sampling: dict
    """
    if not isinstance(dict_sampling, dict):
        raise HyperDriveRehydrateException._with_error(
            AzureMLError.create(
                InvalidType, exp="dict", obj="dict_sampling", actual=scrubbed_data,
                target="dict_sampling"
            )
        )

    if "name" not in dict_sampling:
        raise HyperDriveRehydrateException._with_error(
            AzureMLError.create(
                InvalidKeyInDict, key="name", dict="dict_sampling"
            )
        )

    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)

    for cls in clsmembers:
        if not hasattr(cls[1], 'SAMPLING_NAME'):
            continue

        if cls[1].SAMPLING_NAME.lower() == dict_sampling["name"].lower():
            return cls[1]._from_dict(dict_sampling)

    raise HyperDriveConfigException._with_error(
        AzureMLError.create(
            RehydrateUnknownSampling
        )
    )


class HyperParameterSampling(ABC):
    """Abstract base class for all hyperparameter sampling algorithms.

    This class encapsulates the hyperparameter space, the sampling method, and additional properties for derived
    sampling classes: :class:`azureml.train.hyperdrive.BayesianParameterSampling`,
    :class:`azureml.train.hyperdrive.GridParameterSampling`, and
    :class:`azureml.train.hyperdrive.RandomParameterSampling`.

    :param sampling_method_name: The name of the sampling method.
    :type sampling_method_name: str
    :param parameter_space: A dictionary containing each parameter and its distribution.
    :type parameter_space: dict
    :param properties: A dictionary with additional properties for the algorithm.
    :type properties: dict
    :param supported_distributions: A list of the supported distribution methods. The default None indicates all
            distributions are supported as described in module :mod:`azureml.train.hyperdrive.parameter_expressions`.
    :type supported_distributions: set[str]
    """

    def __init__(self, sampling_method_name, parameter_space, properties=None,
                 supported_distributions=None, distributions_validators=None):
        """Initialize HyperParameterSampling.

        :param sampling_method_name: The name of the sampling method.
        :type sampling_method_name: str
        :param parameter_space: A dictionary containing each parameter and its distribution.
        :type parameter_space: dict
        :param properties: A dictionary with additional properties for the algorithm.
        :type properties: dict
        :param supported_distributions: A list of the supported distribution methods. The default of None indicates all
                distributions are supported as described in module parameter_expressions.
        :type supported_distributions: set[str]
        :param distributions_validators: A dictionary that maps a distribution name to a function that validates
                if it is a valid distribution for the sampling method used. The default None indicates that
                no particular validators are needed.
        :type distributions_validators: dict
        """
        self._sampling_method_name = sampling_method_name
        self._parameter_space = parameter_space
        self._properties = properties
        self._supported_distributions = supported_distributions
        self._distributions_validators = distributions_validators
        self._validate_supported_distributions()

    def to_json(self):
        """Return JSON representing the hyperparameter sampling object.

        :returns: JSON formatted sampling policy.
        :rtype: str
        """
        definition = \
            {
                "name": self._sampling_method_name,
                "parameter_space": self._parameter_space
            }
        if self._properties:
            definition["properties"] = self._properties

        return definition

    def _validate_supported_distributions(self):
        if self._supported_distributions:
            for distribution in self._parameter_space.values():
                if isinstance(distribution, list) and distribution[0] not in self._supported_distributions:
                    supported_distribution_list = ", ".join(self._supported_distributions)
                    raise HyperDriveConfigException._with_error(
                        AzureMLError.create(
                            InvalidConfigSetting, obj="This sampling method",
                            condition="only the following distributions: [{}]"
                                      .format(supported_distribution_list),
                            target="slack_factor, slack_amount"
                        )
                    )
                if self._distributions_validators is not None and \
                        distribution[0] in self._distributions_validators:
                    validation_result = self._distributions_validators[distribution[0]](distribution)
                    if not validation_result[0]:
                        raise HyperDriveConfigException._with_error(
                            AzureMLError.create(
                                DistributionValidationFailure, err=validation_result[1]
                            )
                        )

    def __eq__(self, other):
        """Define equality in terms of the equality of the properties."""
        return self.__dict__ == other.__dict__

    @staticmethod
    def _validate_dict_sampling(dict_sampling, name):
        if not isinstance(dict_sampling, dict) or \
                "name" not in dict_sampling or \
                dict_sampling["name"].lower() != name.lower():
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    DictValidationInvalidArgument, method="_validate_dict_sampling",
                    target="dict_sampling"
                )
            )

        if "parameter_space" not in dict_sampling:
            raise HyperDriveRehydrateException._with_error(
                AzureMLError.create(
                    InvalidKeyInDict, key="parameter_space", dict="dict_sampling"
                )
            )

    @staticmethod
    def _choice_validator(choice_definition):
        """Validate the choice distribution arguments.

        :param choice_definition: Distribution to validate.
        :return: a tuple <True, None> if the choice distribution is correctly defined, or <False, Message> if not.
        """
        choice_values = choice_definition[1][0]
        if choice_values:
            for value in choice_values:
                if not type(value) in (int, str, float):
                    return False, "'choice' values should be 'int', 'string' or 'float'."

            choice_types = [type(c) for c in choice_values]
            if choice_types.count(str) % len(choice_types) != 0:
                return False, "Either all or none of the 'choice' values should be 'str' type."
        else:
            return False, "At least one 'choice' value is required."

        return True, None


class RandomParameterSampling(HyperParameterSampling):
    """Defines random sampling over a hyperparameter search space.

    .. remarks::
        In this sampling algorithm, parameter values are chosen from a set of discrete values or a distribution over
        a continuous range. Examples of functions you can use include:
        :func:`azureml.train.hyperdrive.parameter_expressions.choice`,
        :func:`azureml.train.hyperdrive.parameter_expressions.uniform`,
        :func:`azureml.train.hyperdrive.parameter_expressions.loguniform`,
        :func:`azureml.train.hyperdrive.parameter_expressions.normal`, and
        :func:`azureml.train.hyperdrive.parameter_expressions.lognormal`.
        For example,

        .. code-block:: python

            {
                "init_lr": uniform(0.0005, 0.005),
                "hidden_size": choice(0, 100, 120, 140, 180)
            }

        This will define a search space with two parameters, ``init_lr`` and ``hidden_size``.
        The ``init_lr`` can have a uniform distribution with 0.0005 as a minimum value and 0.005 as a maximum value,
        and the ``hidden_size`` will be a choice of [80, 100, 120, 140, 180].

        For more information about using RandomParameter sampling, see the tutorial
        `Tune hyperparameters for your model
        <https://docs.microsoft.com/azure/machine-learning/how-to-tune-hyperparameters#define-search-space>`__.

    :param parameter_space: A dictionary containing each parameter and its distribution.
                            The dictionary key is the name of the parameter.
    :type parameter_space: dict
    :param properties: A dictionary with additional properties for the algorithm.
    :type properties: dict
    """

    SAMPLING_NAME = "RANDOM"

    def __init__(self, parameter_space, properties=None):
        """Initialize RandomParameterSampling.

        :param parameter_space: A dictionary containing each parameter and its distribution.
                                The dictionary key is the name of the parameter.
        :type parameter_space: dict
        :param properties: A dictionary with additional properties for the algorithm.
        :type properties: dict
        """
        super().__init__(RandomParameterSampling.SAMPLING_NAME, parameter_space, properties)

    @staticmethod
    def _from_dict(dict_sampling):
        HyperParameterSampling._validate_dict_sampling(dict_sampling, RandomParameterSampling.SAMPLING_NAME)

        return RandomParameterSampling(parameter_space=dict_sampling["parameter_space"])


class GridParameterSampling(HyperParameterSampling):
    """Defines grid sampling over a hyperparameter search space.

    .. remarks::
        In this sampling algorithm, parameter values are chosen from discrete values. You can use the
        :func:`azureml.train.hyperdrive.parameter_expressions.choice` function to generate discrete
        values. For example:

        .. code-block:: python

            {
            "lr": choice(1, 2, 3),
            "batch": choice(8, 9)
            }

        This will define a search space with two parameters, ``lr`` and ``batch``.
        ``lr`` can have one of the values [1, 2, 3], and ``batch`` a value one of the values [8, 9].

        You can also create discrete hyperparameters using a distribution. For more
        information, see the tutorial `Tune hyperparameters for your model
        <https://docs.microsoft.com/azure/machine-learning/how-to-tune-hyperparameters#define-search-space>`__.

    :param parameter_space: A dictionary containing each parameter and its distribution.
                            The dictionary key is the name of the parameter. Only
                            :func:`azureml.train.hyperdrive.parameter_expressions.choice` is supported for
                            GridParameter sampling.
    :type parameter_space: dict
    """

    SAMPLING_NAME = "GRID"

    def __init__(self, parameter_space, properties=None):
        """Initialize GridParameterSampling.

        :param parameter_space: A dictionary containing each parameter and its distribution.
                                The dictionary key is the name of the parameter. Only
                                ``choice`` is supported for GridParameter sampling.
        :type parameter_space: dict
        """
        supported_distributions = {'choice'}
        # We are performing validation in Hyperdrive ParameterExpressionValidation
        distributions_validators = None
        super().__init__(GridParameterSampling.SAMPLING_NAME,
                         parameter_space,
                         supported_distributions=supported_distributions,
                         distributions_validators=distributions_validators,
                         properties=properties)

    @staticmethod
    def _from_dict(dict_sampling):
        HyperParameterSampling._validate_dict_sampling(dict_sampling,
                                                       GridParameterSampling.SAMPLING_NAME)

        return GridParameterSampling(parameter_space=dict_sampling["parameter_space"])


class BayesianParameterSampling(HyperParameterSampling):
    r"""Defines Bayesian sampling over a hyperparameter search space.

    Bayesian sampling tries to intelligently pick the next sample of hyperparameters,
    based on how the previous samples performed, such that the new sample improves
    the reported primary metric.

    .. remarks::
        Note that when using Bayesian sampling, the number of concurrent runs has an impact
        on the effectiveness of the tuning process. Typically, a smaller number of concurrent
        runs leads to better sampling convergence. That is because some runs start without
        fully benefiting from runs that are still running.

        .. note:: Bayesian sampling does not support early termination policies. When using Bayesian parameter \
            sampling, use :class:`azureml.train.hyperdrive.NoTerminationPolicy`, set early termination policy to \
            None, or leave off the ``early_termination_policy`` parameter.

        For more information about using BayesianParameter sampling, see the tutorial
        `Tune hyperparameters for your model
        <https://docs.microsoft.com/azure/machine-learning/how-to-tune-hyperparameters#define-search-space>`__.

    :param parameter_space: A dictionary containing each parameter and its distribution.
                            The dictionary key is the name of the parameter. Note that only
                            :func:`azureml.train.hyperdrive.parameter_expressions.choice`,
                            :func:`azureml.train.hyperdrive.parameter_expressions.quniform`, and
                            :func:`azureml.train.hyperdrive.parameter_expressions.uniform`
                            are supported for Bayesian optimization.
    :type parameter_space: dict
    """

    SAMPLING_NAME = "BayesianOptimization"

    def __init__(self, parameter_space, properties=None):
        """Initialize BayesianParameterSampling.

        :param parameter_space: A dictionary containing each parameter and its distribution.
                                The dictionary key is the name of the parameter. Note that only choice,
                                quniform, and uniform are supported for Bayesian optimization.
        :type parameter_space: dict
        """
        if parameter_space is None:
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidConfigSetting, obj="BayesianParameterSampling",
                    condition="parameter_space to not be None or empty.",
                    target="parameter_space"
                )
            )

        supported_distributions = {'choice', 'quniform', 'uniform'}
        distributions_validators = {'choice': self._choice_validator,
                                    'quniform': self._bayesian_quniform_validator}
        super().__init__(BayesianParameterSampling.SAMPLING_NAME,
                         parameter_space,
                         supported_distributions=supported_distributions,
                         distributions_validators=distributions_validators,
                         properties=properties)

    @staticmethod
    def _bayesian_quniform_validator(quniform_definition):
        """Validate the quniform distribution arguments for bayesian sampling.

        :param quniform_definition: Distribution to validate.
        :return: a tuple <True, None> if the choice distribution is correctly defined, or <False, Message> if not.
        """
        choice_values = quniform_definition[1]

        for item in choice_values:
            if type(item) not in [int]:
                return False, "Expected quniform arguments to be int."

        low = choice_values[0]
        high = choice_values[1]
        q = choice_values[2]

        if (high - low) / q > 100000:
            return False, "Too many discrete points for quniform distribution. Use larger q or uniform instead."

        return True, None

    @staticmethod
    def _from_dict(dict_sampling):
        HyperParameterSampling._validate_dict_sampling(dict_sampling,
                                                       BayesianParameterSampling.SAMPLING_NAME)

        return BayesianParameterSampling(parameter_space=dict_sampling["parameter_space"])
