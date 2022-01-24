# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines a common interface for training optimizers."""
import torch
import torch.optim
from abc import ABC

from azureml.automl.dnn.vision.common import constants, distributed_utils
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException, AutoMLVisionValidationException
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.trainer.optimize_parameters import SgdOptimizerParameters, \
    AdamOptimizerParameters
from torch.optim.optimizer import Optimizer
from torch.tensor import Tensor

from typing import Any, cast, Dict, Iterable, Optional, Union

logger = get_logger(__name__)


class BaseOptimizerWrapper(ABC):
    """Class that defines a common interface for all optimizers."""

    def __init__(self, model_parameters: Union[Iterable[Tensor], Iterable[dict]],
                 settings: Dict[str, Any]) -> None:
        """
        :param model_parameters: Model parameters to be optimized
        :type model_parameters: pytorch model parameters
        :param settings: dictionary containing settings for training
        :type settings: dict
        """
        self._optimizer: Optional[Optimizer] = None

    @property
    def optimizer(self) -> Optimizer:
        """Get the optimizer

        :return: Pytorch Optimizer
        :rtype: Pytorch Optimizer
        """
        self._optimizer = cast(Optimizer, self._optimizer)
        return self._optimizer

    @property
    def state_dict(self) -> Any:
        """Returns the state of the optimizer as a dictionary.

        :return dictionary with the object state
        :rtype dict
        """
        self._optimizer = cast(Optimizer, self._optimizer)
        return self._optimizer.state_dict()

    # TODO: Ignoring type check as mypy is getting confused with the parent class' method
    @property
    def load_state_dict(self, state_dict: Dict[Any, Any]) -> None:  # type: ignore[misc]
        """Loads the optimizer state.

        :param state_dict: dictionary containing the state of the optimizer.
        :type state_dict: dict
        """
        self._optimizer = cast(Optimizer, self._optimizer)
        self._optimizer.load_state_dict(state_dict)


class SGDWrapper(BaseOptimizerWrapper):
    """Wraps Stochastic Gradient Descent Optimizer."""

    def __init__(self, model_parameters: Union[Iterable[Tensor], Iterable[dict]],
                 settings: Dict[str, Any]) -> None:
        """
        :param model_parameters: Model parameters to be optimized
        :type model_parameters: pytorch model parameters
        :param settings: dictionary containing settings for training
        :type settings: dict
        """

        sgd_parameters = SgdOptimizerParameters(settings)

        # adjust learning_rate by multiplying by get_world_size() for multi-gpu
        self._learning_rate = sgd_parameters.learning_rate * distributed_utils.get_world_size()
        self._weight_decay = sgd_parameters.weight_decay
        self._momentum = sgd_parameters.momentum
        self._nesterov = sgd_parameters.nesterov

        self._optimizer = torch.optim.SGD(filter(lambda p: p.requires_grad, model_parameters),
                                          lr=self._learning_rate,
                                          momentum=self._momentum,
                                          weight_decay=self._weight_decay,
                                          nesterov=self._nesterov)


class ADAMWrapper(BaseOptimizerWrapper):
    """Wraps Adam (and AdamW) Optimizer."""

    def __init__(self, model_parameters: Union[Iterable[Tensor], Iterable[dict]],
                 settings: Dict[str, Any]) -> None:
        """
        :param model_parameters: Model parameters to be optimized
        :type model_parameters: pytorch model parameters
        :param settings: dictionary containing settings for training
        :type settings: dict
        """

        adam_parameters = AdamOptimizerParameters(settings)

        # adjust learning_rate by multiplying by get_world_size() for multi-gpu
        self._learning_rate = adam_parameters.learning_rate * distributed_utils.get_world_size()
        self._weight_decay = adam_parameters.weight_decay
        self._beta1 = adam_parameters.beta1
        self._beta2 = adam_parameters.beta2
        self._amsgrad = adam_parameters.amsgrad

        if adam_parameters.optimizer_type == constants.OptimizerType.ADAMW:
            self._optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model_parameters),
                                                lr=self._learning_rate,
                                                betas=(self._beta1, self._beta2),
                                                weight_decay=self._weight_decay,
                                                amsgrad=self._amsgrad)
        else:
            self._optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, model_parameters),
                                               lr=self._learning_rate,
                                               betas=(self._beta1, self._beta2),
                                               weight_decay=self._weight_decay,
                                               amsgrad=self._amsgrad)


class OptimizerFactory:
    """Factory class that creates optimizer wrappers."""

    _optimizers_dict = {
        constants.OptimizerType.SGD: SGDWrapper,
        constants.OptimizerType.ADAM: ADAMWrapper,
        constants.OptimizerType.ADAMW: ADAMWrapper
    }

    def get_optimizer(self, model: torch.nn.Module, settings: Dict[str, Any]) -> Optimizer:
        """Create an optimizer

        :param model: Model to be optimized
        :type model: pytorch model
        :param settings: dictionary containing settings for training
        :type settings: dict
        :returns: Pytorch Optimizer
        :rtype: Pytorch Optimizer
        """

        optimizer_type = settings[constants.TrainingLiterals.OPTIMIZER]

        if optimizer_type not in OptimizerFactory._optimizers_dict:
            raise AutoMLVisionValidationException("Optimizer type not supported.", has_pii=False)

        # classifying parameters into subgroups
        pg0, pg1, pg2 = [], [], []  # pg0 for conv/fc weights, pg1 for bn weights and pg2 for biases
        for k, v in model.named_modules():
            # It iterates over modules. For instance, 'layer0.bn1' module can have both bn bias and bn weight.
            if hasattr(v, 'bias') and isinstance(v.bias, torch.nn.Parameter):
                pg2.append(v.bias)  # biases

            # FrozenBatchNorm2d is used (instead of BatchNorm2d) in faster-rcnn, mask-rcnn and retinanet,
            # due to small batch size which makes the batch statistics very poor and degrades performance.
            # https://github.com/pytorch/vision/blob/master/torchvision/ops/misc.py
            # Thus, we ignore isinstance(v, FrozenBatchNorm2d) since those bn params have requires_grad False
            if isinstance(v, torch.nn.BatchNorm2d):
                pg1.append(v.weight)  # no decay
            elif hasattr(v, 'weight') and isinstance(v.weight, torch.nn.Parameter):
                pg0.append(v.weight)  # apply decay
            else:
                # if there are still un-classified parameters from Conv2d or Linear,
                # you need to check model architecture and update the above logic accordingly.
                if isinstance(v, torch.nn.Conv2d) or isinstance(v, torch.nn.Linear):
                    msg = "There are still un-classified parameters from Conv2d or Linear. Please check your model."
                    logger.error(msg)
                    raise AutoMLVisionSystemException(msg, has_pii=False)

        optimizer = OptimizerFactory._optimizers_dict[optimizer_type](pg0, settings).optimizer

        # add pg1 (bn weights) and pg2 (biases) without weight_decay to optimizer
        optimizer.add_param_group({'params': filter(lambda p: p.requires_grad, pg1), 'weight_decay': 0.})
        optimizer.add_param_group({'params': filter(lambda p: p.requires_grad, pg2), 'weight_decay': 0.})
        return optimizer


def setup_optimizer(model: torch.nn.Module, settings: Dict[str, Any]) -> Optimizer:
    """Convenience function that wraps creating an optimizer.

    :param model: Model to be optimized
    :type model: Pytorch model
    :param settings: dictionary containing settings for training
    :type settings: dict
    :returns: Pytorch optimizer
    :rtype: Pytorch optimizer
    """

    optimizer_factory = OptimizerFactory()

    return optimizer_factory.get_optimizer(model, settings)
