# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
# from ._utils import _C
from PMTD.maskrcnn_benchmark import _C

from PMTD.maskrcnn_benchmark.apex.apex import amp

# Only valid with fp32 inputs - give AMP the hint
print(_C)
nms = amp.float_function(_C.nms)

# nms.__doc__ = """
# This function performs Non-maximum suppresion"""
