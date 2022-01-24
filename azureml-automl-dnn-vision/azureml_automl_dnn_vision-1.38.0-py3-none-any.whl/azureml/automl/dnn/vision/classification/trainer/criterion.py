# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines a criterion for loss functions"""
import torch
from torch import nn
from typing import Union


def _get_criterion(multilabel: bool = False,
                   class_weights: torch.Tensor = None) -> Union[nn.BCEWithLogitsLoss, nn.CrossEntropyLoss]:
    """Get torch criterion.

    :param multilabel: flag indicating if it is a multilabel problem or not.
    :type multilabel: bool
    :param class_weights: class-level rescaling weights
    :type class_weights: torch.Tensor
    :return: torch criterion
    :rtype: object from one of torch.nn criterion classes
    """
    criterion: Union[nn.BCEWithLogitsLoss, nn.CrossEntropyLoss]
    if multilabel:
        # https://pytorch.org/docs/stable/generated/torch.nn.BCEWithLogitsLoss.html#torch.nn.BCEWithLogitsLoss
        criterion = nn.BCEWithLogitsLoss(pos_weight=class_weights)  # Type: nn.BCEWithLogitsLoss
    else:
        criterion = nn.CrossEntropyLoss(weight=class_weights)  # Type: nn.CrossEntropyLoss
    return criterion
