# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" PyTorch utility functions
    Note: This code is mainly adapted from https://github.com/ultralytics/yolov5/blob/master/utils/torch_utils.py
"""

import math
import torch
from torch.tensor import Tensor
import torch.backends.cudnn as cudnn
import torch.nn as nn
import torch.nn.functional as F
from typing import cast


def torch_init_seeds(seed=0):
    """Set torch randomization seed

    :param seed: torch randomization seed
    :type seed: int
    """
    torch.manual_seed(seed)

    # Speed-reproducibility tradeoff https://pytorch.org/docs/stable/notes/randomness.html
    if seed == 0:  # slower, more reproducible
        cudnn.deterministic = True
        cudnn.benchmark = False
    else:  # faster, less reproducible
        cudnn.deterministic = False
        cudnn.benchmark = True


def config_modules(model):
    """ Configure modules given a model

    :param model: Yolo Model
    :type model: <class 'azureml.automl.dnn.vision.object_detection_yolo.models.yolo.Model'>
    """
    for m in model.modules():
        t = type(m)
        if t is nn.Conv2d:
            pass  # nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
        elif t is nn.BatchNorm2d:
            m.eps = 1e-3
            m.momentum = 0.03
        elif t in [nn.LeakyReLU, nn.ReLU, nn.ReLU6]:
            m.inplace = True


def fuse_conv_and_bn(conv, bn):
    """ Fuse conv and bn layers into conv layer https://tehnokv.com/posts/fusing-batchnorm-and-conv/

    :param conv: Convolution layer
    :type conv: <class 'torch.nn.modules.conv.Conv2d'>
    :param bn: Batch Norm layer
    :type bn: <class 'torch.nn.modules.batchnorm.BatchNorm2d'>
    """

    with torch.no_grad():
        # init
        fusedconv = nn.Conv2d(conv.in_channels,
                              conv.out_channels,
                              kernel_size=conv.kernel_size,
                              stride=conv.stride,
                              padding=conv.padding,
                              bias=True).to(conv.weight.device)

        # prepare filters
        w_conv = conv.weight.clone().view(conv.out_channels, -1)
        w_bn = torch.diag(bn.weight.div(torch.sqrt(bn.eps + bn.running_var)))
        fusedconv.weight.copy_(torch.mm(w_bn, w_conv).view(fusedconv.weight.size()))

        # prepare spatial bias
        b_conv = torch.zeros(conv.weight.size(0), device=conv.weight.device) if conv.bias is None else conv.bias
        b_bn = bn.bias - bn.weight.mul(bn.running_mean).div(torch.sqrt(bn.running_var + bn.eps))
        fusedconv.bias = cast(Tensor, fusedconv.bias)
        fusedconv.bias.copy_(torch.mm(w_bn, b_conv.reshape(-1, 1)).reshape(-1) + b_bn)

        return fusedconv


def scale_img(img, ratio=1.0, same_shape=False):
    """ Scale an Image by ratio

    :param img: Image in [batch, 3, height, width])
    :type img: <class 'torch.Tensor'>
    :param ratio: ratio
    :type ratio: float
    :param same_shape: same_shape
    :type same_shape: bool
    :return: scaled image
    :rtype: <class 'torch.Tensor'>
    """

    if ratio == 1.0:
        return img
    else:
        h, w = img.shape[2:]
        s = (int(h * ratio), int(w * ratio))  # new size
        img = F.interpolate(img, size=s, mode='bilinear', align_corners=False)  # resize
        if not same_shape:  # pad/crop img
            gs = 32  # (pixels) grid size
            h, w = [math.ceil(x * ratio / gs) * gs for x in (h, w)]
        return F.pad(img, [0, w - s[1], 0, h - s[0]], value=0.447)  # value = imagenet mean
