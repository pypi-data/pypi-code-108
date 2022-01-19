"""This module offers a replacement for detectrons's `build_backbone` function.
"""
from typing import Union, Tuple

from detectron2.modeling import build_backbone as d2_build_backbone
from detectron2.modeling.backbone.fpn import FPN
from detectron2.config import CfgNode
from detectron2.layers import ShapeSpec
from torch import nn

from .timm_backbones import TimmBackbone


def build_backbone(cfg: CfgNode, input_shape: Union[ShapeSpec, None]=None) -> Tuple[nn.Module, Tuple[float], Tuple[float]]:
    '''Functions similar to detectrons's `build_backbone` function.

    In addition it returns the correct pixel mean and std for the backbond.
    For timm backbones the mean and std can be retrieved form the created model.
    For d2 backbones the mean and std from the cfg are returned.

    Parameters
    ----------
    cfg: CfgNode
        config
    input_shape: None or ShapeSpec, optinal, default=None
        If None it is expected to be Shapespec(channels=3).

    '''
    backbone = d2_build_backbone(cfg, input_shape)
    if isinstance(backbone, TimmBackbone):
        return backbone, backbone.pixel_mean, backbone.pixel_std
    elif isinstance(backbone, FPN) and isinstance(backbone.bottom_up, TimmBackbone):
        return backbone, backbone.bottom_up.pixel_mean, backbone.bottom_up.pixel_std
    else:
        return backbone, cfg.MODEL.PIXEL_MEAN, cfg.MODEL.PIXEL_STD
