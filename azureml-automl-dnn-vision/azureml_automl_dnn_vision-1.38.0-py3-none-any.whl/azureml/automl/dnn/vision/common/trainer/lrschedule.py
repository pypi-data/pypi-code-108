# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines a common interface for learning rate schedulers."""

from abc import ABC
from enum import Enum
import math
import torch.optim
from typing import Any, Dict, Type
from torch.optim.lr_scheduler import _LRScheduler

from azureml.automl.dnn.vision.common import constants
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException
from azureml.automl.dnn.vision.common.trainer.lrschedule_parameters import StepLRSchedulerParameters, \
    WarmUpCosineLRSchedulerParameters


class LRSchedulerUpdateType(Enum):
    """Type indicating when lr scheduler should be updated during training."""
    BATCH = 0
    EPOCH = 1


class BaseLRSchedulerWrapper(ABC):
    """Class that provides a common interface for all learning
    rate schedulers"""

    def __init__(self, optimizer: torch.optim.Optimizer,
                 batches_per_epoch: int,
                 settings: Dict[str, Any]) -> None:
        """
        :param optimizer: Optimizer the scheduler will operate on
        :type optimizer: Pytorch optimizer
        :param batches_per_epoch: Number of batches in an epoch
        :type: batches_per_epoch: int
        :param settings: dictionary containing settings for training
        :type settings: dict
        """
        self._lr_scheduler: Any = None
        self._update_type: Any = None

    @property
    def lr_scheduler(self) -> _LRScheduler:
        """Get the learning rate scheduler.

        :return: learning rate scheduler
        :rtype: pytoch learning rate scheduler
        """
        return self._lr_scheduler

    @property
    def update_type(self) -> Any:
        """Get the scheduler update type.

        :return: scheduler update type.
        :rtype: LRSchedulerUpdateType
        """
        return self._update_type


class StepLRWrapper(BaseLRSchedulerWrapper):
    """Wrapper for Step Learning Rate Scheduler."""

    def __init__(self, optimizer: torch.optim.Optimizer,
                 batches_per_epoch: int,
                 settings: Dict[str, Any]) -> None:
        """
        :param optimizer: Optimizer the scheduler will operate on
        :type optimizer: Pytorch optimizer
        :param batches_per_epoch: Number of batches in an epoch
        :type: batches_per_epoch: int
        :param settings: dictionary containing settings for training.
        :type settings: dict
        """

        lr_scheduler_parameters = StepLRSchedulerParameters(settings)

        self._step_size = lr_scheduler_parameters.step_size
        self._gamma = lr_scheduler_parameters.gamma

        self._lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer,
                                                             step_size=self._step_size,
                                                             gamma=self._gamma)
        self._update_type = LRSchedulerUpdateType.EPOCH


class WarmUpCosineLRWrapper(BaseLRSchedulerWrapper):
    """Wrapper for warmUp cosine learning rate scheduler. Linearly increases the lr from 0 to `initial_learning_rate`
    set in optimizer over `warmup_steps` number of training steps. Decreases the lr from `initial_learning_rate`
    over remaining `total_steps - warmup_steps` steps following a cosine curve.
    If `cycles` is 0.5, lr reaches 0 by end of total_steps.
    If `cycles` < 0.5, lr decreases following cosine curve, but doesn't reach 0 at end of total_steps.
    Please note that if `cycles` > 0.5, lr starts to increase after decrease to 0.
    """

    def __init__(self, optimizer: torch.optim.Optimizer,
                 batches_per_epoch: int,
                 settings: Dict[str, Any]) -> None:
        """
        :param optimizer: Optimizer the scheduler will operate on
        :type optimizer: Pytorch optimizer
        :param batches_per_epoch: Number of batches in an epoch
        :type: batches_per_epoch: int
        :param settings: dictionary containing settings for training.
        :type settings: dict
        """

        lr_scheduler_parameters = WarmUpCosineLRSchedulerParameters(batches_per_epoch, settings)

        self._warmup_steps = lr_scheduler_parameters.warmup_steps
        self._total_steps = lr_scheduler_parameters.total_steps
        self._cycles = lr_scheduler_parameters.cycles

        self._lr_scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=self._lr_lambda)
        self._update_type = LRSchedulerUpdateType.BATCH

    def _lr_lambda(self, step: int) -> float:
        """Function to return the lr multiplicative factor to be used at step

        Note: This code has been copied from here:
        https://huggingface.co/transformers/v1.2.0/_modules/pytorch_transformers/optimization.html#WarmupCosineSchedule

        :param step: Current step
        :type step: Int
        :return: lr multiplicative factor
        :rtype: Float
        """
        if step < self._warmup_steps:
            return float(step) / float(max(1.0, self._warmup_steps))
        # progress after warmup
        progress = float(step - self._warmup_steps) / float(max(1, self._total_steps - self._warmup_steps))
        return max(0.0, 0.5 * (1. + math.cos(math.pi * float(self._cycles) * 2.0 * progress)))


class LRSchedulerFactory:
    """Factory class that creates learning rate scheduler wrappers."""

    _scheduler_dict: Dict[str, Type[BaseLRSchedulerWrapper]] = {
        constants.LrSchedulerType.STEP: StepLRWrapper,
        constants.LrSchedulerType.WARMUP_COSINE: WarmUpCosineLRWrapper
    }

    def get_lr_scheduler(self, optimizer: torch.optim.Optimizer,
                         batches_per_epoch: int,
                         settings: Dict[str, Any]) -> BaseLRSchedulerWrapper:
        """Construct and return a learning rate scheduler wrapper.

        :param optimizer: Optimizer the scheduler will operate on
        :type optimizer: Pytorch optimizer
        :param batches_per_epoch: Number of batches in an epoch
        :type: batches_per_epoch: int
        :param settings: dictionary containing settings for training
        :type settings: dict
        :returns: Learning rate scheduler wrapper
        :rtype: BaseLRSchedulerWrapper
        """

        lr_scheduler_type_str = settings[constants.TrainingLiterals.LR_SCHEDULER]

        if lr_scheduler_type_str not in LRSchedulerFactory._scheduler_dict:
            raise AutoMLVisionValidationException("Scheduler type not supported.", has_pii=False)

        scheduler_class: Type[BaseLRSchedulerWrapper] = LRSchedulerFactory._scheduler_dict[lr_scheduler_type_str]

        return scheduler_class(optimizer, batches_per_epoch, settings)


def setup_lr_scheduler(optimizer: torch.optim.Optimizer,
                       batches_per_epoch: int,
                       settings: Dict[str, Any]) -> BaseLRSchedulerWrapper:
    """Convenience function that wraps creating a learning rate scheduler.

    :param optimizer: Optimizer the scheduler will operate on
    :type optimizer: Pytorch optimizer
    :param batches_per_epoch: Number of batches in an epoch
    :type: batches_per_epoch: int
    :param settings: dictionary containing settings for training
    :type settings: dict
    :returns: Learning rate scheduler wrapper
    :rtype: BaseLRSchedulerWrapper
    """

    scheduler_factory = LRSchedulerFactory()

    return scheduler_factory.get_lr_scheduler(optimizer, batches_per_epoch, settings)
