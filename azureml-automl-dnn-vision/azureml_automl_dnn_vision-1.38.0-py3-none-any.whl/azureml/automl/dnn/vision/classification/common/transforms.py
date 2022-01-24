# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines transformation functions for the package."""
import torch

from torchvision import transforms
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException


def _get_common_train_transforms(crop_size) -> transforms.Compose:
    """Get train transformation that works for most common classification cases.

    :param crop_size: final input size to crop the image to
    :type crop_size: int
    :return: Transform object for training
    :rtype: object
    """
    return transforms.Compose([
        transforms.RandomResizedCrop(crop_size),
        transforms.RandomHorizontalFlip(),
        transforms.RandomChoice([
            transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.4),
            transforms.Lambda(_identity),
        ]),
        transforms.ToTensor(),
        transforms.Lambda(_make_3d_tensor),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])


def _get_common_valid_transforms(resize_to=None, crop_size=None) -> transforms.Compose:
    """Get validation transformation which is just cropping the input after a resize.

    :param resize_to: square size to resize to
    :type resize_to: int
    :param crop_size: final input size to crop the image to
    :type crop_size: int
    :return: Transform object for validation
    :rtype: object
    """
    if resize_to is None or crop_size is None:
        raise AutoMLVisionValidationException('one of crop_size or input_size is None', has_pii=False)

    return transforms.Compose([
        transforms.Resize(resize_to),
        transforms.CenterCrop(crop_size),
        transforms.ToTensor(),
        transforms.Lambda(_make_3d_tensor),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])


def _identity(x) -> torch.Tensor:
    """Identity transformation.

    :param x: input tensor
    :type x: torch.Tensor
    :return: return the input as is
    :rtype: torch.Tensor
    """
    return x


def _make_3d_tensor(x) -> torch.Tensor:
    """This function is for images that have less channels.

    :param x: input tensor
    :type x: torch.Tensor
    :return: return a tensor with the correct number of channels
    :rtype: torch.Tensor
    """
    return x if x.shape[0] == 3 else x.expand((3, x.shape[1], x.shape[2]))
