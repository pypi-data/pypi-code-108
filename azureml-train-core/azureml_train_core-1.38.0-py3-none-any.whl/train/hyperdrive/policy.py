# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The early termination policies.

Early termination policies enable canceling poor-performing runs before they complete.  A poor-performing run
is one that is not doing as well in comparison to the best-performing run with respect to a primary metric.
"""
import inspect
import sys
from abc import ABC

from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore
from azureml.train.hyperdrive.error_definition import (
    DictValidationInvalidArgument, InvalidConfigSetting, InvalidKeyInDict,
    InvalidType, RehydratePolicyNotFound)
from azureml.train.hyperdrive.exceptions import (HyperDriveConfigException,
                                                 HyperDriveRehydrateException)

scrubbed_data = "[Scrubbed]"


def _policy_from_dict(dict_policy):
    """Construct a Policy object from a dictionary.

    The dictionary is supposed to come from a previous run that's retrieved from the cloud.
    This is an internal utility method.

    :param dict_policy: A dictionary of the policy.
    :type dict_policy: dict
    """
    if not isinstance(dict_policy, dict):
        raise HyperDriveConfigException._with_error(
            AzureMLError.create(
                InvalidType, exp="dict", obj="dict_policy", actual=scrubbed_data,
                target="dict_policy"
            )
        )
    if "name" not in dict_policy:
        raise HyperDriveRehydrateException._with_error(
            AzureMLError.create(
                InvalidKeyInDict, key="name", dict="dict_policy"
            )
        )

    clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)

    for cls in clsmembers:
        if hasattr(cls[1], "POLICY_NAME") and \
                cls[1].POLICY_NAME.lower() == dict_policy["name"].lower():
            return cls[1]._from_dict(dict_policy)

    raise HyperDriveConfigException._with_error(
        AzureMLError.create(
            RehydratePolicyNotFound, policy=dict_policy["name"]
        )
    )


class EarlyTerminationPolicy(ABC):
    """Abstract base class for all early termination policies.

    .. remarks::
        Early termination policies can be applied to HyperDrive runs. A run is cancelled when the criteria
        of a specified policy are met. Examples of policies you can use include:

        * :class:`azureml.train.hyperdrive.BanditPolicy`
        * :class:`azureml.train.hyperdrive.MedianStoppingPolicy`
        * :class:`azureml.train.hyperdrive.TruncationSelectionPolicy`

        Use the :class:`azureml.train.hyperdrive.NoTerminationPolicy` to specify that no early
        termination policy is to be applied for a run.

        Use the ``policy`` parameter of the :class:`azureml.train.hyperdrive.HyperDriveConfig` class to
        specify a policy.
    """

    def __init__(self, name, properties=None):
        """Initialize an early termination policy.

        :param name: The name of the policy.
        :type name: str
        :param properties: A JSON serializable object of properties.
        :type properties: dict
        """
        self._name = name
        self._properties = properties

    def to_json(self):
        """Return JSON representing the termination policy.

        :returns: JSON formatted termination policy.
        :rtype: str
        """
        termination_policy = {
            "name": self._name,
        }

        if self._properties is not None:
            termination_policy["properties"] = self._properties

        return termination_policy

    def __eq__(self, other):
        """Define equality in terms of the equality of the properties."""
        return self.__dict__ == other.__dict__

    @staticmethod
    def _validate_dict_policy(dict_policy, name):
        if not isinstance(dict_policy, dict) or \
                "name" not in dict_policy or \
                dict_policy["name"].lower() != name.lower():
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    DictValidationInvalidArgument, method="_validate_dict_policy",
                    target="dict_policy"
                )
            )


class BanditPolicy(EarlyTerminationPolicy):
    """Defines an early termination policy based on slack criteria, and a frequency and delay interval for evaluation.

    .. remarks::
        The Bandit policy takes the following configuration parameters:

        * ``slack_factor``: The amount of slack allowed with respect to the best performing training run. This factor
          specifies the slack as a ratio.
        * ``slack_amount``: The amount of slack allowed with respect to the best performing training run. This factor
          specifies the slack as an absolute amount.
        * ``evaluation_interval``: Optional. The frequency for applying the policy. Each time the training script
          logs the primary metric counts as one interval.
        * `` delay_evaluation``:  Optional. The number of intervals to delay policy evaluation. Use this parameter
          to avoid premature termination of training runs. If specified, the policy applies every multiple of
          ``evaluation_interval`` that is greater than or equal to ``delay_evaluation``.

        Any run that doesn't fall within the slack factor or slack amount of the evaluation metric
        with respect to the best performing run will be terminated.

        Consider a Bandit policy with ``slack_factor`` = 0.2 and ``evaluation_interval`` = 100.
        Assume that run X is the currently best performing run with an AUC (performance metric) of 0.8 after 100
        intervals. Further, assume the best AUC reported for a run is Y. This policy compares the value
        (Y + Y * 0.2) to 0.8, and if smaller, cancels the run. If ``delay_evaluation`` = 200, then the
        first time the policy will be applied is at interval 200.

        Now, consider a Bandit policy with ``slack_amount`` = 0.2 and ``evaluation_interval`` = 100.
        If Run 3 is the currently best performing run with an AUC (performance metric) of 0.8 after 100 intervals,
        then any run with an AUC less than 0.6 (0.8 - 0.2) after 100 iterations will be terminated.
        Similarly, the ``delay_evaluation`` can also be used to delay the first termination policy
        evaluation for a specific number of sequences.

        For more information about applying early termination policies, see `Tune hyperparameters for your model
        <https://docs.microsoft.com/azure/machine-learning/how-to-tune-hyperparameters>`__.

    :param slack_factor: The ratio used to calculate the allowed distance from the best performing experiment run.
    :type slack_factor: float
    :param slack_amount: The absolute distance allowed from the best performing run.
    :type slack_amount: float
    :param evaluation_interval: The frequency for applying the policy.
    :type evaluation_interval: int
    :param delay_evaluation: The number of intervals for which to delay the first policy evaluation.
                             If specified, the policy applies every multiple of ``evaluation_interval``
                             that is greater than or equal to ``delay_evaluation``.
    :type delay_evaluation: int
    """

    POLICY_NAME = "Bandit"

    def __init__(self, evaluation_interval=1, slack_factor=None, slack_amount=None, delay_evaluation=0):
        """Initialize a BanditPolicy with slack factor, slack_amount, and evaluation interval.

        :param slack_factor: The ratio used to calculate the allowed distance from the best performing experiment run.
        :type slack_factor: float
        :param slack_amount: The absolute distance allowed from the best performing run.
        :type slack_amount: float
        :param evaluation_interval: The frequency for applying the policy.
        :type evaluation_interval: int
        :param delay_evaluation: The number of intervals for which to delay the first policy evaluation.
                                 If specified, the policy applies every multiple of ``evaluation_interval``
                                 that is greater than or equal to ``delay_evaluation``.
        :type delay_evaluation: int
        """
        if (slack_factor is None and slack_amount is None) or (slack_factor and slack_amount):
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidConfigSetting, obj="Bandit termination policy",
                    condition="exactly one of slack factor or slack amount to be set.",
                    target="slack_factor, slack_amount"
                )
            )

        if not isinstance(evaluation_interval, int):
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidType, exp="int", obj="evaluation_interval", actual=scrubbed_data,
                    target="evaluation_interval"
                )
            )

        if not isinstance(delay_evaluation, int):
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidType, exp="int", obj="delay_evaluation", actual=scrubbed_data,
                    target="delay_evaluation"
                )
            )

        policy_config = {
            "evaluation_interval": evaluation_interval,
            "delay_evaluation": delay_evaluation
        }

        if slack_factor:
            policy_config["slack_factor"] = slack_factor
        else:
            policy_config["slack_amount"] = slack_amount

        super().__init__(BanditPolicy.POLICY_NAME, policy_config)
        self._slack_factor = slack_factor
        self._evaluation_interval = evaluation_interval
        self._delay_evaluation = delay_evaluation

    @property
    def slack_factor(self):
        """Return the slack factor with respect to the best performing training run.

        :return: The slack factor.
        :rtype: float
        """
        return self._slack_factor

    @property
    def evaluation_interval(self):
        """Return the evaluation interval value.

        :return: The evaluation interval.
        :rtype: int
        """
        return self._evaluation_interval

    @property
    def delay_evaluation(self):
        """Return the number of sequences for which the first evaluation is delayed.

        :return: The delay evaluation.
        :rtype: int
        """
        return self._delay_evaluation

    @staticmethod
    def _from_dict(dict_policy):
        EarlyTerminationPolicy._validate_dict_policy(dict_policy, BanditPolicy.POLICY_NAME)

        if "properties" not in dict_policy:
            raise HyperDriveRehydrateException._with_error(
                AzureMLError.create(
                    InvalidKeyInDict, key="properties", dict="dict_policy"
                )
            )

        properties = dict_policy["properties"]

        return BanditPolicy(properties.get("evaluation_interval"), properties.get("slack_factor"),
                            properties.get("slack_amount"), properties.get("delay_evaluation"))


class MedianStoppingPolicy(EarlyTerminationPolicy):
    """Defines an early termination policy based on running averages of the primary metric of all runs.

    .. remarks::
        The Median Stopping policy computes running averages across all runs and cancels runs whose best performance
        is worse than the median of the running averages. Specifically, a run will be canceled at interval N
        if its best primary metric reported up to interval N is worse than the median of the running averages
        for intervals 1:N across all runs.

        The Median Stopping policy takes the following optional configuration parameters:

        * ``evaluation_interval``: The frequency for applying the policy. Each time the training script logs the
          primary metric counts as one interval.
        * `` delay_evaluation``: The number of intervals to delay policy evaluation. Use this parameter to avoid
          premature termination of training runs. If specified, the policy applies every multiple of
          ``evaluation_interval`` that is greater than or equal to ``delay_evaluation``.

        This policy is inspired from the research publication `Google Vizier: A Service for Black-Box Optimization
        <https://research.google.com/pubs/pub46180.html>`_.

        If you are looking for a conservative policy that provides savings without terminating promising jobs,
        you can use a Median Stopping Policy with ``evaluation_interval`` 1 and ``delay_evaluation 5``. These are
        conservative settings, that can provide approximately 25%-35% savings with no loss on primary metric (based
        on our evaluation data).

    :param evaluation_interval: The frequency for applying the policy.
    :type evaluation_interval: int
    :param delay_evaluation: The number of intervals for which to delay the first policy evaluation.
                             If specified, the policy applies every multiple of ``evaluation_interval``
                             that is greater than or equal to ``delay_evaluation``.
    :type delay_evaluation: int
    """

    POLICY_NAME = "MedianStopping"

    def __init__(self, evaluation_interval=1, delay_evaluation=0):
        """Initialize a MedianStoppingPolicy.

        :param evaluation_interval: The frequency for applying the policy.
        :type evaluation_interval: int
        :param delay_evaluation: The number of intervals for which to delay the first policy evaluation.
                                 If specified, the policy applies every multiple of ``evaluation_interval``
                                 that is greater than or equal to ``delay_evaluation``.
        :type delay_evaluation: int
        """
        if not isinstance(evaluation_interval, int):
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidType, exp="int", obj="evaluation_interval", actual=scrubbed_data,
                    target="evaluation_interval"
                )
            )

        if not isinstance(delay_evaluation, int):
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidType, exp="int", obj="delay_evaluation", actual=scrubbed_data,
                    target="delay_evaluation"
                )
            )

        policy_config = {
            "evaluation_interval": evaluation_interval,
            "delay_evaluation": delay_evaluation
        }

        super().__init__(MedianStoppingPolicy.POLICY_NAME, policy_config)
        self._evaluation_interval = evaluation_interval
        self._delay_evaluation = delay_evaluation

    @property
    def evaluation_interval(self):
        """Return evaluation interval value.

        :return: The evaluation interval.
        :rtype: int
        """
        return self._evaluation_interval

    @property
    def delay_evaluation(self):
        """Return the value for the number of sequences the first evaluation is delayed.

        :return: The delay evaluation.
        :rtype: int
        """
        return self._delay_evaluation

    @staticmethod
    def _from_dict(dict_policy):
        EarlyTerminationPolicy._validate_dict_policy(dict_policy, MedianStoppingPolicy.POLICY_NAME)

        if "properties" not in dict_policy:
            raise HyperDriveRehydrateException._with_error(
                AzureMLError.create(
                    InvalidKeyInDict, key="properties", dict="dict_policy"
                )
            )

        properties = dict_policy["properties"]

        return MedianStoppingPolicy(properties.get("evaluation_interval"),
                                    properties.get("delay_evaluation"))


class TruncationSelectionPolicy(EarlyTerminationPolicy):
    """Defines an early termination policy that cancels a given percentage of runs at each evaluation interval.

    .. remarks::
        This policy periodically cancels the given percentage of runs that rank the lowest for their performance
        on the primary metric. The policy strives for fairness in ranking the runs by accounting for improving
        model performance with training time. When ranking a relatively young run, the policy uses the
        corresponding (and earlier) performance of older runs for comparison. Therefore, runs aren't terminated
        for having a lower performance because they have run for less time than other runs.

        The Truncation Selection policy takes the following configuration parameters:

        * ``truncation_percentage``: The percentage of lowest performing runs to terminate at each evaluation
          interval.
        * ``evaluation_interval``: The frequency for applying the policy. Each time the training script logs the
          primary metric counts as one interval.
        * `` delay_evaluation``: The number of intervals to delay policy evaluation. Use this parameter to avoid
          premature termination of training runs. If specified, the policy applies every multiple of
          ``evaluation_interval`` that is greater than or equal to ``delay_evaluation``.

        For example, when evaluating a run at a interval N, its performance is only compared with the performance
        of other runs up to interval N even if they reported metrics for intervals greater than N.

    :param truncation_percentage: The percentage of runs to cancel at each evaluation interval.
    :type truncation_percentage: int
    :param evaluation_interval: The frequency for applying the policy.
    :type evaluation_interval: int
    :param delay_evaluation: The number of intervals for which to delay the first policy evaluation.
                                If specified, the policy applies every multiple of ``evaluation_interval``
                                that is greater than or equal to ``delay_evaluation``.
    :type delay_evaluation: int
    """

    POLICY_NAME = "TruncationSelection"

    def __init__(self, truncation_percentage, evaluation_interval=1, delay_evaluation=0):
        """Initialize a TruncationSelectionPolicy.

        :param truncation_percentage: The percentage of runs to cancel at each evaluation interval.
        :type truncation_percentage: int
        :param evaluation_interval: The frequency for applying the policy.
        :type evaluation_interval: int
        :param delay_evaluation: The number of intervals for which to delay the first policy evaluation.
                                 If specified, the policy applies every multiple of ``evaluation_interval``
                                 that is greater than or equal to ``delay_evaluation``.
        :type delay_evaluation: int
        """
        if not isinstance(truncation_percentage, int):
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidType, exp="int", obj="truncation_percentage", actual=scrubbed_data,
                    target="truncation_percentage"
                )
            )

        if truncation_percentage < 1 or truncation_percentage > 99:
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidConfigSetting, obj="truncation_percentage",
                    condition="value to be between 1 and 99.", target="truncation_percentage"
                )
            )

        if not isinstance(evaluation_interval, int):
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidType, exp="int", obj="evaluation_interval", actual=scrubbed_data,
                    target="evaluation_interval"
                )
            )

        if not isinstance(delay_evaluation, int):
            raise HyperDriveConfigException._with_error(
                AzureMLError.create(
                    InvalidType, exp="int", obj="delay_evaluation", actual=scrubbed_data,
                    target="delay_evaluation"
                )
            )

        policy_config = {
            "evaluation_interval": evaluation_interval,
            "delay_evaluation": delay_evaluation,
            "truncation_percentage": truncation_percentage,
            "exclude_finished_jobs": False
        }

        super().__init__(TruncationSelectionPolicy.POLICY_NAME, policy_config)
        self._truncation_percentage = truncation_percentage
        self._evaluation_interval = evaluation_interval
        self._delay_evaluation = delay_evaluation

    @property
    def truncation_percentage(self):
        """Return truncation percentage value.

        :return: The truncation percentage.
        :rtype: int
        """
        return self._truncation_percentage

    @property
    def evaluation_interval(self):
        """Return evaluation interval value.

        :return: The evaluation interval.
        :rtype: int
        """
        return self._evaluation_interval

    @property
    def delay_evaluation(self):
        """Return the value for number of sequences the first evaluation is delayed.

        :return: The delay evaluation.
        :rtype: int
        """
        return self._delay_evaluation

    @staticmethod
    def _from_dict(dict_policy):
        EarlyTerminationPolicy._validate_dict_policy(dict_policy, TruncationSelectionPolicy.POLICY_NAME)

        if "properties" not in dict_policy:
            raise HyperDriveRehydrateException._with_error(
                AzureMLError.create(
                    InvalidKeyInDict, key="properties", dict="dict_policy"
                )
            )

        properties = dict_policy["properties"]

        return TruncationSelectionPolicy(properties.get("truncation_percentage"),
                                         properties.get("evaluation_interval"),
                                         properties.get("delay_evaluation"))


class NoTerminationPolicy(EarlyTerminationPolicy):
    """Specifies that no early termination policy is applied.

    Each run will execute until completion.
    """

    POLICY_NAME = "Default"

    def __init__(self):
        """Initialize NoTerminationPolicy."""
        super().__init__(NoTerminationPolicy.POLICY_NAME)

    @staticmethod
    def _from_dict(dict_policy):
        EarlyTerminationPolicy._validate_dict_policy(dict_policy, NoTerminationPolicy.POLICY_NAME)

        return NoTerminationPolicy()
