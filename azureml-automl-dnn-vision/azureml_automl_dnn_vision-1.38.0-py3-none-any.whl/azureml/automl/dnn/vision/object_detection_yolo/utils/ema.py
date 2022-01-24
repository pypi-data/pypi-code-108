# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" PyTorch utility functions
    Note: This code is mainly adapted from https://github.com/ultralytics/yolov5/blob/master/utils/torch_utils.py
"""

import math
import torch

from copy import deepcopy


def _copy_attr(a, b, include=(), exclude=()):
    """ Copy attributes from b to a, options to only include [...] and to exclude [...] """
    for k, v in b.__dict__.items():
        if (len(include) and k not in include) or k.startswith('_') or k in exclude:
            continue
        else:
            setattr(a, k, v)


class ModelEMA:
    """ Model Exponential Moving Average from https://github.com/rwightman/pytorch-image-models
    Keep a moving average of everything in the model state_dict (parameters and buffers).
    This is intended to allow functionality like
    https://www.tensorflow.org/api_docs/python/tf/train/ExponentialMovingAverage
    A smoothed version of the weights is necessary for some training schemes to perform well.
    This class is sensitive where it is initialized in the sequence of model init,
    GPU assignment and distributed training wrappers.
    """

    def __init__(self, model: torch.nn.Module, decay: float = 0.9999, updates: int = 0) -> None:
        """ Create EMA

        :param model: Model
        :type model: <class 'azureml.automl.dnn.vision.object_detection_yolo.models.yolo.Model'>
        :param decay: decay
        :type decay: float
        :param device: device type
        :type device: string
        """
        self.ema = deepcopy(model).eval()
        self.updates = updates  # number of EMA updates
        self.decay = lambda x: decay * (1 - math.exp(-x / 2000))  # decay exponential ramp (to help early epochs)
        for p in self.ema.parameters():
            p.requires_grad_(False)

    def update(self, model):
        """ Update EMA parameters

        :param model: Model
        :type model: <class 'azureml.automl.dnn.vision.object_detection_yolo.models.yolo.Model'>
        """
        with torch.no_grad():
            self.updates += 1
            d = self.decay(self.updates)

            msd = model.state_dict()
            for k, v in self.ema.state_dict().items():
                if v.dtype.is_floating_point:
                    v *= d
                    v += (1. - d) * msd[k].detach()

    def update_attr(self, model, include=(), exclude=('process_group', 'reducer')):
        """ Update EMA attributes

        :param model: Model
        :type model: <class 'azureml.automl.dnn.vision.object_detection_yolo.models.yolo.Model'>
        :param include: options to include for attribute update
        :type include: <class 'tuple'>
        :param exclude: options to exclude for attribute update
        :type exclude: <class 'tuple'>
        """
        _copy_attr(self.ema, model, include, exclude)
