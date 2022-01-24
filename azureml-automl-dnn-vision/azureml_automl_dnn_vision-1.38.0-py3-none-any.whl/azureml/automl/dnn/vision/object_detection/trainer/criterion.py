# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Classes that define a standard loss function interface."""

from abc import ABC, abstractmethod
from ..common import constants

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException


class BaseCriterionWrapper(ABC):
    """Base class that defines required loss behavior."""

    @abstractmethod
    def evaluate(self, model, images, targets):
        """Computes loss from model, batch of images and targets.
        Must be implemented in any instationation of criterion.

        :param model: Object detection model
        :type model: BaseObjectDetectionModelWrapper type object
        :param images: Batch of images
        :type images: Pytorch tensor of N images
        :param targets: Batch of image labels
        :type targets: Pytorch tensor of N labels
        :return: Loss on image batch
        :rtype: Float Tensor
        """
        pass


class LossFromModelCriterion(BaseCriterionWrapper):
    """Loss function for models that output loss."""

    def evaluate(self, model, images, targets):
        """Computes loss from model, batch of images and targets.
        Must be implemented in any instationation of criterion.
        For models that output loss like faster rcnn, retinanet, mask rcnn.

        :param model: Object detection model
        :type model: BaseObjectDetectionModelWrapper type object
        :param images: Batch of images
        :type images: Pytorch tensor of N images
        :param targets: Batch of image labels
        :type targets: Pytorch tensor of N labels
        :return: Loss dict on image batch
        :rtype: Float Tensor
        """

        losses = model(images, targets)
        return losses


class CriterionFactory:
    """Helper class that produces loss functions for models."""
    _criterion_dict = {
        constants.CriterionNames.LOSS_FROM_MODEL: LossFromModelCriterion
    }

    def _get_criterion(self, criterion_name):
        """Creates a loss function based on name.
        :param criterion_name: Name of the loss function to be created
        :type criterion_name: str
        :returns: Loss function wrapper
        :rtype: Criterion object derived from BaseCriterionWrapper
        """
        if criterion_name not in CriterionFactory._criterion_dict:
            raise AutoMLVisionValidationException("criterion_name not supported.", has_pii=False)

        return CriterionFactory._criterion_dict[criterion_name]()


def setup_criterion(criterion_name):
    """Convenience function that wraps criterion factory behavior.

    :param criterion_name: Names of the loss function
    :type criterion_name: string
    :returns: Loss function wrapper
    :rtype: Criterion object derived from BaseCriterionWrapper
    """

    criterion_factory = CriterionFactory()

    return criterion_factory._get_criterion(criterion_name)
