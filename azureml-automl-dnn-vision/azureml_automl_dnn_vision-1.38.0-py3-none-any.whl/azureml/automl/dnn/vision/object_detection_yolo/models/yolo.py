# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" Yolov5 model
    Note: This code is mainly adapted from https://github.com/ultralytics/yolov5/blob/master/models/yolo.py
"""
import copy
import math
import os
import torch
import torch.nn as nn
from typing import Any, Dict, List, Tuple, Union
from torch.tensor import Tensor

from .common import Conv, Bottleneck, SPP, Focus, BottleneckCSP, Concat
from ..utils.torch_utils import config_modules, scale_img, fuse_conv_and_bn
from ..utils.utils import make_divisible, check_anchor_order

import azureml._vendor.ruamel.yaml as yaml
from azureml.automl.dnn.vision.common.logging_utils import get_logger

logger = get_logger(__name__)


class Detect(nn.Module):
    """ yolo detection layer """
    stride: Union[Any, Tensor] = None  # strides computed during build

    def __init__(self, nc: int = 80, anchors: Tuple = (), ch: Tuple = ()) -> None:
        """
        :param nc: number of classes
        :type nc: int
        :param anchors: anchors
        :type anchors: list
        """
        super(Detect, self).__init__()
        self.nc = nc  # number of classes
        self.no = nc + 5  # number of outputs per anchor
        self.nl = len(anchors)  # number of detection layers
        self.na = len(anchors[0]) // 2  # number of anchors
        self.grid = [torch.zeros(1)] * self.nl  # init grid
        a = torch.tensor(anchors).float().view(self.nl, -1, 2)
        self.register_buffer('anchors', a)  # shape(nl,na,2)
        self.register_buffer('anchor_grid', a.clone().view(self.nl, 1, -1, 1, 1, 2))  # shape(nl,1,na,1,1,2)
        self.m = nn.ModuleList(nn.Conv2d(x, self.no * self.na, 1) for x in ch)  # output conv

    def forward(self, x):
        """ forward function """
        z = []  # inference output
        for i in range(self.nl):
            x[i] = self.m[i](x[i])  # conv
            bs, _, ny, nx = x[i].shape  # x(bs,255,20,20) to x(bs,3,20,20,85)
            x[i] = x[i].view(bs, self.na, self.no, ny, nx).permute(0, 1, 3, 4, 2).contiguous()

            if not self.training:  # inference
                if self.grid[i].shape[2:4] != x[i].shape[2:4]:
                    self.grid[i] = self._make_grid(nx, ny).to(x[i].device)

                y = x[i].sigmoid()
                y[..., 0:2] = (y[..., 0:2] * 2. - 0.5 + self.grid[i].to(x[i].device)) * self.stride[i]  # xy
                y[..., 2:4] = (y[..., 2:4] * 2) ** 2 * self.anchor_grid[i]  # wh
                z.append(y.view(bs, -1, self.no))

        return x if self.training else (torch.cat(z, 1), x)

    @staticmethod
    def _make_grid(nx=20, ny=20):
        yv, xv = torch.meshgrid([torch.arange(ny), torch.arange(nx)])
        return torch.stack((xv, yv), 2).view((1, 1, ny, nx, 2)).float()


class Model(nn.Module):
    """ yolo model """

    def __init__(self, model_cfg: Any = 'yolov5m.yaml', ch: int = 3, nc: int = 0) -> None:
        """
        :param model_cfg: yaml file for model definition
        :type model_cfg: string
        :param ch: input channels
        :type ch: int
        :param nc: number of classes
        :type nc: int
        """
        super(Model, self).__init__()
        if isinstance(model_cfg, dict):
            self.yaml: Dict[str, Any] = model_cfg  # model dict
        else:  # is *.yaml
            with open(model_cfg) as f:
                self.yaml = yaml.load(f, Loader=yaml.Loader)  # model dict

        # Define model
        if nc and nc != self.yaml['nc']:
            if not isinstance(model_cfg, dict):
                logger.info("[Overriding {} nc={} with nc={}]".format(model_cfg.split(os.sep)[-1],
                                                                      self.yaml['nc'], nc))
            self.yaml['nc'] = nc
        self.ch = ch
        self.model, self.save = parse_model(copy.deepcopy(self.yaml), ch=[self.ch])  # model, savelist, ch_out

        # Build strides, anchors
        m = self.model[-1]  # Detect()
        if isinstance(m, Detect):
            s = 128  # 2x min stride
            m.stride = torch.tensor([s / x.shape[-2] for x in self.forward(torch.zeros(1, ch, s, s))])  # forward
            m.anchors /= m.stride.view(-1, 1, 1)
            check_anchor_order(m)
            self.stride = m.stride
            self._initialize_biases()  # only run once

        # Init weights, biases
        config_modules(self)
        self._initialize_biases()  # only run once

    def forward(self, x, augment=False):
        """ forward function """
        if augment:
            # TODO: need to validate this path for Test-Time Augmentation (TTA)
            # https://github.com/ultralytics/yolov5/issues/303
            img_size = x.shape[-2:]  # height, width
            s = [1, 0.83, 0.67]  # scales
            f = [None, 3, None]  # flips (2-ud, 3-lr)
            y = []  # outputs
            for si, fi in zip(s, f):
                xi = scale_img(x.flip(fi) if fi else x, si)
                yi = self.forward_once(xi)[0]  # forward
                yi[..., :4] /= si  # de-scale
                if fi == 2:
                    yi[..., 1] = img_size[0] - yi[..., 1]  # de-flip ud
                elif fi == 3:
                    yi[..., 0] = img_size[1] - yi[..., 0]  # de-flip lr
                y.append(yi)
            return torch.cat(y, 1), None  # augmented inference, train
        else:
            return self.forward_once(x)  # single-scale inference, train

    def forward_once(self, x):
        """ forward function """
        y: List[Any] = []  # output
        for m in self.model:
            if m.f != -1:  # if not from previous layer
                x = y[m.f] if isinstance(m.f, int) else [x if j == -1 else y[j] for j in m.f]  # from earlier layers

            x = m(x)  # run
            y.append(x if m.i in self.save else None)  # save output
        return x

    def _initialize_biases(self, cf=None):
        """ initialize biases into Detect(), cf is class frequency """
        # cf = torch.bincount(torch.tensor(np.concatenate(dataset.labels, 0)[:, 0]).long(), minlength=nc) + 1.
        m = self.model[-1]  # Detect() module
        for mi, s in zip(m.m, m.stride):  # from
            b = mi.bias.view(m.na, -1)  # conv.bias(255) to (3,85)
            b[:, 4] += math.log(8 / (640 / s) ** 2)  # obj (8 objects per 640 image)
            b[:, 5:] += math.log(0.6 / (m.nc - 0.99)) if cf is None else torch.log(cf / cf.sum())  # cls
            mi.bias = torch.nn.Parameter(b.view(-1), requires_grad=True)

    def fuse(self):
        """ fuse model Conv2d() + BatchNorm2d() layers """
        for m in self.model.modules():
            if type(m) is Conv:
                m.conv = fuse_conv_and_bn(m.conv, m.bn)  # update conv
                delattr(m, 'bn')  # remove batchnorm
                m.forward = m.forward_no_bn  # update forward

    def state_dict(self, destination=None, prefix='', keep_vars=False):
        """Get the state dictionary from pytorch model

        :param destination: refer to PytTorch doc
        :type destination: dict
        :param prefix: refer to PytTorch doc
        :type prefix: str
        :param keep_vars: refer to PytTorch doc
        :type keep_vars: bool
        :return: State dictionary
        :rtype: dict
        """
        return self.model.state_dict(destination=destination, prefix=prefix, keep_vars=keep_vars)


def parse_model(md, ch):
    """
    :param md: model definition dictionary from yaml file
    :type md: dict
    :param ch: input channels in [3]
    :type ch: list
    """
    anchors, nc, gd, gw = md['anchors'], md['nc'], md['depth_multiple'], md['width_multiple']
    na = (len(anchors[0]) // 2) if isinstance(anchors, list) else anchors  # number of anchors
    no = na * (nc + 5)  # number of outputs = anchors * (classes + 5)

    layers, c2 = [], ch[-1]  # layers, ch out
    save: List[Any] = []  # savelist
    for i, (f, n, m, args) in enumerate(md['backbone'] + md['head']):  # from, number, module, args
        m = eval(m) if isinstance(m, str) else m  # eval strings
        for j, a in enumerate(args):
            try:
                args[j] = eval(a) if isinstance(a, str) else a  # eval strings
            except Exception:
                pass

        n = max(round(n * gd), 1) if n > 1 else n  # depth gain
        if m in [Conv, Bottleneck, SPP, Focus, BottleneckCSP]:
            c1, c2 = ch[f], args[0]
            c2 = make_divisible(c2 * gw, 8) if c2 != no else c2

            args = [c1, c2, *args[1:]]
            if m in [BottleneckCSP]:
                args.insert(2, n)
                n = 1
        elif m is nn.BatchNorm2d:
            args = [ch[f]]
        elif m is Concat:
            c2 = sum([ch[-1 if x == -1 else x + 1] for x in f])
        elif m is Detect:
            args.append([ch[x + 1] for x in f])
            if isinstance(args[1], int):  # number of anchors
                args[1] = [list(range(args[1] * 2))] * len(f)
        else:
            c2 = ch[f]

        m_ = nn.Sequential(*[m(*args) for _ in range(n)]) if n > 1 else m(*args)  # module
        t = str(m)[8:-2].replace('__main__.', '')  # module type
        np = sum([x.numel() for x in m_.parameters()])  # number params
        m_.i, m_.f, m_.type, m_.np = i, f, t, np  # attach index, 'from' index, type, number params
        save.extend(x % i for x in ([f] if isinstance(f, int) else f) if x != -1)  # append to savelist
        layers.append(m_)
        ch.append(c2)
    return nn.Sequential(*layers), sorted(save)
