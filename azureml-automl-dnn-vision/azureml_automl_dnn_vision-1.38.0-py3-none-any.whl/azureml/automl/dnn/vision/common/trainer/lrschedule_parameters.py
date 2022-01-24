# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Classes that contain all the parameters associated with training
models. """
from typing import Dict, Any
from azureml.automl.dnn.vision.common.constants import TrainingLiterals


class StepLRSchedulerParameters:
    """Class that contains all parameters needed by Step learning rate scheduler."""

    def __init__(self, settings: Dict[str, Any]) -> None:
        """
        :param settings: dictionary containing settings for training. Currently supported include:
          -step_size: Number of steps before changing learning rate
          -gamma: Rate at which to decrease the learning rate
        :type settings: dict
        """

        self._lr_scheduler_type: str = settings[TrainingLiterals.LR_SCHEDULER]
        # specific to step lr
        self._step_size: int = settings[TrainingLiterals.STEP_LR_STEP_SIZE]
        self._gamma: int = settings[TrainingLiterals.STEP_LR_GAMMA]

    @property
    def lr_scheduler_type(self) -> str:
        """Get lr_scheduler type

        :returns: lr_scheduler type
        :rtype: str
        """
        return self._lr_scheduler_type

    @property
    def step_size(self) -> int:
        """
        :return: step size
        :rtype: Int
        """
        return self._step_size

    @property
    def gamma(self) -> int:
        """
        :return: gamma
        :rtype: Int
        """
        return self._gamma


class WarmUpCosineLRSchedulerParameters:
    """Class that contains all parameters needed by warmup cosine learning rate scheduler."""

    def __init__(self, batches_per_epoch: int, settings: Dict[str, Any]) -> None:
        """
        :param settings: dictionary containing settings for training. Currently supported include:
          -warmup_steps: Number of steps to linearly increase the learning rate (warmup)
          -total_steps: Total number of steps in training.
          -cycles: A factor by which learning rate follows the cosine curve after warmup.
        :type settings: dict
        """

        self._lr_scheduler_type: str = settings[TrainingLiterals.LR_SCHEDULER]
        # specific to warmup cosine lr
        self._warmup_steps: int = batches_per_epoch * settings[TrainingLiterals.WARMUP_COSINE_LR_WARMUP_EPOCHS]
        self._total_steps: int = batches_per_epoch * settings[TrainingLiterals.NUMBER_OF_EPOCHS]
        self._cycles: float = settings[TrainingLiterals.WARMUP_COSINE_LR_CYCLES]

    @property
    def lr_scheduler_type(self) -> str:
        """Get lr_scheduler type

        :returns: lr_scheduler type
        :rtype: str
        """
        return self._lr_scheduler_type

    @property
    def warmup_steps(self) -> int:
        """
        :return: warmup steps.
        :rtype: Int
        """
        return self._warmup_steps

    @property
    def total_steps(self) -> int:
        """
        :return: total steps.
        :rtype: Int
        """
        return self._total_steps

    @property
    def cycles(self) -> float:
        """
        :return: Cycles.
        :rtype: Float
        """
        return self._cycles
