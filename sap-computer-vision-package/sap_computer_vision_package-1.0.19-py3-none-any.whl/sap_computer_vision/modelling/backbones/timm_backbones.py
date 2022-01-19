"""This module provides classes and functions to use all models form the
timm library https://github.com/rwightman/pytorch-image-models
as backbones.
"""
import logging
from typing import Union, List, Dict

import torch

from detectron2.modeling import BACKBONE_REGISTRY, Backbone
from detectron2.layers import ShapeSpec
from detectron2.modeling.backbone.fpn import LastLevelMaxPool, FPN
try:
    import timm
    _timm_available = True
except ImportError:
    _timm_available = False


logger = logging.getLogger(__name__)


class TimmBackbone(Backbone):
    """Backbone class to wrap timm models as backbones for detectron2.
    """
    def __init__(self,
                 model_name: str,
                 pretrained: bool=True,
                 out_features: Union[None, List[str]]=None,
                 features_only: bool=True):
        """Create backbone based on a timm model.

        Normal detectron backbone weights are initialized using e.g. the
        trainer checkpointer or trainer.resume_or_load. timm-Models are
        initialized during creation. The 'pretrained' enables/disables
        to loading process of pretrained weights.

        Parameters
        ----------
        model_name: str
            Name of the model. Check timm documentation for options.
        pretrained: bool, optinal, default=True
            Load pretrained weights.
        out_features: None, optional, default=None
            Name of backbones layer included in the backbone output.
            If None the default layers specified by the timm library
            is used.
        features_only: bool, optional, default=True
            To use the models as backbones the head used during the pretraining
            should be removed. Many models form the timm library can be
            explicitly created as feature extractors using the
            'features_only' parameter during model creation.
            All other models are created as classifiers and the classification
            head is chopped off after creation. This is automatically done
            during init of the class if features_only=False. As a general rule
            always try to features_only=True. If it crashed during creationg
            try features_only=False. Check:
            https://rwightman.github.io/pytorch-image-models/feature_extraction/
            for more details.
        """
        if not _timm_available:
            raise ImportError('Missing dependency. Install \'timm\' to use a TimmBackbone (`pip install timm`).')
        super(TimmBackbone, self).__init__()
        self.model = timm.create_model(model_name,
                                       pretrained=pretrained,
                                       features_only=features_only,
                                       out_indices=out_features)
        self.pixel_mean = [x*255 for x in self.model.default_cfg['mean']]
        self.pixel_std = [x*255 for x in self.model.default_cfg['std']]
        self.features_only = features_only
        if features_only:
            self._output_names = []
            self._output_shapes = {}
            for info in self.model.feature_info.info:
                name = info['module']
                self._output_names.append(name)
                self._output_shapes[name] = ShapeSpec(channels=info['num_chs'], stride=info['reduction'])
        else:
            self.model.reset_classifier(0)
            self._output_names = ['forward_features']
            self._output_shapes = {'forward_features': ShapeSpec(channels=self.model.num_features)}

    def forward(self, x: 'torch.Tensor') -> Dict[str, 'torch.Tensor']:
        """Forward step of the model

        Parameter
        ---------
        x: torch.Tensor
            Images tensors

        Returns
        -------
        Dict of torch.Tensors
            Image features
        """
        model_output = self.model(x)
        if not self.features_only:
            model_output = (model_output, )
        return {k: o_i for k, o_i in zip(self._output_names, model_output)}

    def output_shape(self) -> 'ShapeSpec':
        """
        Returns
        -------
        ShapeSpec
            ShapeSpec of the model output
        """
        return self._output_shapes

    def output_names(self) -> List['str']:
        """
        Returns
        -------
        list of str
            Names of the image features.
            The names are used as keys in the dict returned by the forward step.
        """
        return self._output_names


@BACKBONE_REGISTRY.register()
def build_timm_backbone(cfg, *args, **kwargs) -> 'Backbone':
    """Registered backbone function to create a plain TimmBackbone.

    All options for the Backbone are specified in the config.
    The relevant CfgNodes are cfg.MODEL.TIMM.

    Parameter
    ---------
    cfg: CfgNode
        Config

    Retruns
    -------
    Backbone
    """
    model_args = {
        'model_name': cfg.MODEL.TIMM.NAME,
        'pretrained': cfg.MODEL.TIMM.PRETRAINED,
        'out_features': cfg.MODEL.TIMM.get('OUT_INDICES', None),
        'features_only': cfg.MODEL.TIMM.get('FEATURES_ONLY', True)
    }
    if cfg.INPUT.FORMAT.upper() != 'RGB':
        raise ValueError('Models form `timm` are using images in the RGB ordering!')
    model = TimmBackbone(**model_args)
    fixed_input = model.model.default_cfg.get('fixed_input_size', False)
    cfg_fixed_input =  cfg.INPUT.get('FIXED_IMAGE_SIZE', None)
    if cfg_fixed_input is None and fixed_input:
        logger.warning(f'The backbone expected a fixed input of shape {fixed_input}. `cfg.INPUT.FIXED_IMAGE_SIZE` not set!')
    return model


@BACKBONE_REGISTRY.register()
def build_timm_fpn_backbone(cfg, *args, **kwargs) -> 'Backbone':
    """Registered backbone function to create a TimmBackbone wrapped in a FPN.

    This most probably only works for CNN based models.
    All options for the Backbone are specified in the config.
    The relevant CfgNodes are cfg.MODEL.TIMM and cfg.MODEL.FPN

    Parameter
    ---------
    cfg: CfgNode
        Config

    Retruns
    -------
    Backbone
    """
    if not cfg.MODEL.TIMM.get('FEATURES_ONLY', True):
        raise ValueError('To build a FPN with a timm cnn model as a backbone `MODEL.TIMM.FEATURES_ONLY` '
                         'has to be `True`')
    bottom_up = build_timm_backbone(cfg)
    in_features = bottom_up.output_names()
    out_channels = cfg.MODEL.FPN.OUT_CHANNELS
    backbone = FPN(
        bottom_up=bottom_up,
        in_features=in_features,
        out_channels=out_channels,
        norm=cfg.MODEL.FPN.NORM,
        top_block=LastLevelMaxPool(),
        fuse_type=cfg.MODEL.FPN.FUSE_TYPE,
    )
    return backbone
