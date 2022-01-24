# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" Modules common to various models
    Note: This code is mainly adapted from https://github.com/ultralytics/yolov5/blob/master/models/common.py
"""

import torch
import torch.nn as nn
from typing import Tuple, Optional


def _autopad(k, p=None):  # kernel, padding
    """ Pad to 'same' """
    if p is None:
        p = k // 2 if isinstance(k, int) else [x // 2 for x in k]  # auto-pad
    return p


class Conv(nn.Module):
    """ Standard convolution """

    def __init__(self, c1: int, c2: int, k: int = 1, s: int = 1, p: Optional[int] = None, g: int = 1,
                 act: bool = True) -> None:
        """
        :param c1: ch_in
        :type c1: int
        :param c2: ch_out
        :type c2: int
        :param k: kernel
        :type k: int
        :param s: stride
        :type s: int
        :param p: padding
        :type p: int
        :param g: groups
        :type g: int
        :param act: activation
        :type act: bool
        """
        super(Conv, self).__init__()
        self.conv = nn.Conv2d(c1, c2, k, s, _autopad(k, p), groups=g, bias=False)
        self.bn = nn.BatchNorm2d(c2)
        self.act = nn.Hardswish() if act else nn.Identity()

    def forward(self, x):
        """ forward function """
        return self.act(self.bn(self.conv(x)))

    def forward_no_bn(self, x):
        """ forward function without bach norm """
        return self.act(self.conv(x))


class Bottleneck(nn.Module):
    """ Standard bottleneck """

    def __init__(self, c1: int, c2: int, shortcut: bool = True, g: int = 1, e: float = 0.5) -> None:
        """
        :param c1: ch_in
        :type c1: int
        :param c2: ch_out
        :type c2: int
        :param shortcut: shortcut
        :type shortcut: bool
        :param g: groups
        :type g: int
        :param e: expansion
        :type e: float
        """
        super(Bottleneck, self).__init__()
        c_ = int(c2 * e)  # hidden channels
        self.cv1 = Conv(c1, c_, 1, 1)
        self.cv2 = Conv(c_, c2, 3, 1, g=g)
        self.add = shortcut and c1 == c2

    def forward(self, x):
        """ forward function """
        return x + self.cv2(self.cv1(x)) if self.add else self.cv2(self.cv1(x))


class BottleneckCSP(nn.Module):
    """ CSP Bottleneck https://github.com/WongKinYiu/CrossStagePartialNetworks """

    def __init__(self, c1: int, c2: int, n: int = 1, shortcut: bool = True, g: int = 1, e: float = 0.5) -> None:
        """
        :param c1: ch_in
        :type c1: int
        :param c2: ch_out
        :type c2: int
        :param n: number
        :type n: int
        :param shortcut: shortcut
        :type shortcut: bool
        :param g: groups
        :type g: int
        :param e: expansion
        :type e: float
        """
        super(BottleneckCSP, self).__init__()
        c_ = int(c2 * e)  # hidden channels
        self.cv1 = Conv(c1, c_, 1, 1)
        self.cv2 = nn.Conv2d(c1, c_, 1, 1, bias=False)
        self.cv3 = nn.Conv2d(c_, c_, 1, 1, bias=False)
        self.cv4 = Conv(2 * c_, c2, 1, 1)
        self.bn = nn.BatchNorm2d(2 * c_)  # applied to cat(cv2, cv3)
        self.act = nn.LeakyReLU(0.1, inplace=True)
        self.m = nn.Sequential(*[Bottleneck(c_, c_, shortcut, g, e=1.0) for _ in range(n)])

    def forward(self, x):
        """ forward function """
        y1 = self.cv3(self.m(self.cv1(x)))
        y2 = self.cv2(x)
        return self.cv4(self.act(self.bn(torch.cat((y1, y2), dim=1))))


class SPP(nn.Module):
    """ Spatial pyramid pooling layer used in YOLOv3-SPP """

    def __init__(self, c1: int, c2: int, k: Tuple[int, int, int] = (5, 9, 13)) -> None:
        """
        :param c1: ch_in
        :type c1: int
        :param c2: ch_out
        :type c2: int
        :param k: kernel
        :type k: list
        """
        super(SPP, self).__init__()
        c_ = c1 // 2  # hidden channels
        self.cv1 = Conv(c1, c_, 1, 1)
        self.cv2 = Conv(c_ * (len(k) + 1), c2, 1, 1)
        self.m = nn.ModuleList([nn.MaxPool2d(kernel_size=x, stride=1, padding=x // 2) for x in k])

    def forward(self, x):
        """ forward function """
        x = self.cv1(x)
        return self.cv2(torch.cat([x] + [m(x) for m in self.m], 1))


class Focus(nn.Module):
    """ Focus wh information into c-space """

    def __init__(self, c1: int, c2: int, k: int = 1, s: int = 1, p: Optional[int] = None, g: int = 1,
                 act: bool = True) -> None:
        """
        :param c1: ch_in
        :type c1: int
        :param c2: ch_out
        :type c2: int
        :param k: kernel
        :type k: int
        :param s: stride
        :type s: int
        :param p: padding
        :type p: int
        :param g: groups
        :type g: int
        :param act: activation
        :type act: bool
        """
        super(Focus, self).__init__()
        self.conv = Conv(c1 * 4, c2, k, s, p, g, act)

    def forward(self, x):
        """ forward function
            x(b,c,w,h) -> y(b,4c,w/2,h/2)
        """
        return self.conv(torch.cat([x[..., ::2, ::2], x[..., 1::2, ::2], x[..., ::2, 1::2], x[..., 1::2, 1::2]], 1))


class Concat(nn.Module):
    """ Concatenate a list of tensors along dimension """

    def __init__(self, dimension: int = 1) -> None:
        """
        :param dimension: dimension
        :type dimension: int
        """
        super(Concat, self).__init__()
        self.d = dimension

    def forward(self, x):
        """ forward function """
        return torch.cat(x, self.d)


class Hardswish(nn.Module):
    """ Export-friendly version of nn.Hardswish() for ONNX """
    @staticmethod
    def forward(x):
        """ forward function """
        return x * nn.functional.hardtanh(x + 3, 0., 6.) / 6.
