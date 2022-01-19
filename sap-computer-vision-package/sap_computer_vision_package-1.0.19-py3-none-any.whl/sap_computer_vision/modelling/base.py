"""This module contains the base model used for image classificaiton and
triplet distance learning."""
from typing import Dict, List, Union, Tuple
from collections.abc import Iterable as IsIterable

from detectron2.structures import ImageList
from detectron2.config import CfgNode

import torch
from torch import nn

from .backbones import build_backbone


class ProjectionLayer(nn.Module):
    """Layers used to build the projection head.

    It is fully connected layers with optional dropout and configurable
    activation function.
    """
    def __init__(self,
                 in_size: int,
                 out_size: int,
                 dropout: Union[None, float]=None,
                 activation: Union[None, str, 'nn.Module']=None):
        """Create fully connected layer with dropout and activation.

        Parameters
        ----------
        in_size: int
            Number of input features
        out_size: int
            Number of neurons/output features
        dropout: None or float
            Dropout propability.
            If None dropout is disabled.
        activation: str, nn.Module or None
            Activation function applied to the output.
            If str it has to match the name of an activation function from torch.nn.
            If None no activation function will be used.
        """
        super().__init__()
        self.fc = nn.Linear(in_size, out_size)
        if isinstance(activation, str):
            activation = getattr(nn, activation)
        elif isinstance(activation, nn.Module) or activation is None:
            pass
        else:
            raise ValueError('`activation` has to be either None, the name of the activation or an nn.Module!')
        if activation is not None:
            self.activation = activation()
        else:
            self.activation = nn.Identity()
        if isinstance(dropout, float):
            self.dropout = nn.Dropout(p=dropout)
        else:
            self.dropout = nn.Identity()

    def forward(self, features: 'torch.Tensor') -> 'torch.Tensor':
        """Forward step of the layers.

        Parameter
        ---------
        features: torch.Tensor
            Input features.

        Returns
        -------
        torch.Tensor
            Layer output
        """
        return self.dropout(self.activation(self.fc(features)))


class BaseModel(nn.Module): # pylint: disable=R0902
    """This model is the basis for the ImageClassification and TripletDistancerLerner
    models.
    """
    def __init__(self,  # pylint: disable=R0914, R0912, R0915
                 *,
                 backbone: 'nn.Module',
                 pixel_mean: 'torch.Tensor',
                 pixel_std: 'torch.Tensor',
                 out_dim: Union[None, int]=None,
                 dropout: Union[None, float]=0.5,
                 image_size: Union[None, int, Tuple[int, int]]=None,
                 intermediate_sizes: Union[None, int, List[int]]=None,
                 input_feats: Union[None, List[str]]=None,
                 pooling: Union[bool, str]=True,
                 normalize_output: bool=False,
                 freeze_backbone: bool=False,
                 activation_projection_layer: Union[str, None]='ReLU'):
        """The model uses a backbone model and appends a projection head.
        It supports different options for the projection head.
        - using multiple outputs from the backbone e.g. different levels from a FPN
        - pooling of backbone features
        - normalization of the final output
        - configurable number of fc layers with different activation functions and optional dropout
        - support backbones from the timm's library.

        Parameters
        ----------
        backbone: nn.Module
            Backbone model. Supports all backbones from detectron2 and TimmBackbones.
            See sap_computer_vision.modelling.backbones.timm_backbones for details.
        pixel_mean: torch.Tensor
            Mean pixel values
        pixel_std: torch.Tensor
            Std of the pixel values
        out_dim: None or int, optional, default=None
            Dimensionality of the final layer.
            If None the last layer is nn.Identity
        dropout: float, optional, default=0.5
            Dropout probability between projection head layers.
        image_size: None, int or Tuple[Int, Int], optinal, default=None
            If None input image of different sizes are supported.
            Beware when not using pooling or for backbones that output flat
            feature vectors. The input images need a fixed size and image_size
            cannot be None. If int the height and width of the input image have
            to be equal. If non square images images_size has to be a tuple
            (height, width).
        intermediate_sizes: None, int or List[int], optinal, default=None
            Size of layers between backbone and final output layer.
            If None no intermediate layer is used.
        input_feats: None or List[str], optinal, default=None
            Name of the output features used from the backbone.
            If None the model tries to figure out which features are provided by the
            backbone and uses all.
        pooling: bool or str, optional, default=True
            Pooling of backbone output. Available pooling methods are 'max' and
            'average'. If True the default method 'max' will be used.
        normalize_output: bool, optional, default=True
            Normalize the final model output.
        activation_projection_layer: None or str, optional, default='ReLU'
            Name of the activation function used for the intermediate layers.
            Have to match the name of an activation function form torch.nn.
        """
        super().__init__()
        self.register_buffer("pixel_mean", torch.tensor(pixel_mean).view(-1, 1, 1), False)
        self.register_buffer("pixel_std", torch.tensor(pixel_std).view(-1, 1, 1), False)
        self.image_size = image_size
        self.backbone = backbone
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
        backbone_output = self.backbone.output_shape()
        if input_feats is None:
            input_feats = backbone_output.keys()
        self.used_backbone_feats = input_feats
        self.pooling = pooling
        self.normalize_output = normalize_output
        if isinstance(self.pooling, bool) and self.pooling:
            self.pooling = 'max'
        if isinstance(self.pooling, bool) and not self.pooling:
            self.pooling = None
        elif isinstance(self.pooling, str) and self.pooling in ['max', 'average']:
            pass
        else:
            raise ValueError('`pooling` has to be either bool or str (options: `max`, `average`).')

        feat_size = 0
        if self.pooling is not None:
            for feat in self.used_backbone_feats:
                feat = backbone_output[feat]
                channels = feat.channels
                feat_size += channels
            if self.pooling == 'max':
                self.pooler = nn.AdaptiveMaxPool2d((1,1))
            elif self.pooling == 'average':
                self.pooler = nn.AdaptiveAvgPool2d((1,1))
            else:
                raise ValueError('`pooling` has to be either bool or str (options: `max`, `average`).')
        else:
            if self.image_size is None:
                raise ValueError('When not using `pooling` the input image_size '
                                 'has to be fixed and provided to the model.')
            if isinstance(self.image_size, int):
                height, width = self.image_size, self.image_size
            elif isinstance(self.image_size, IsIterable):
                height, width = self.image_size
            for feat in self.used_backbone_feats:
                feat = backbone_output[feat]
                channels = feat.channels
                stride = feat.stride
                if stride is not None:
                    if not (height % stride == 0 and width % stride == 0):
                        raise ValueError(f'`image_size=({height}, {width})`  hast to be a multiple of {stride}!')
                    feat_size += channels * (height // stride)  * (width  // stride)
                else:
                    feat_size += feat.channels
        if isinstance(intermediate_sizes, int):
            intermediate_sizes = [intermediate_sizes]
        elif intermediate_sizes is None:
            intermediate_sizes = []
        input_size = feat_size
        self.projection_layers = len(intermediate_sizes) if intermediate_sizes is not None else 0
        for i, intermediate_size in enumerate(intermediate_sizes):
            output_size = min(intermediate_size, input_size)
            setattr(self, f'projection_layer_{i+1}', ProjectionLayer(input_size,
                                                                     output_size,
                                                                     activation=activation_projection_layer,
                                                                     dropout=dropout))
            input_size = output_size
        self.out = nn.Identity() if out_dim is None else nn.Linear(input_size, out_dim)
        self.out_dim = input_size if out_dim is None else out_dim


    def forward(self,
                batched_inputs: List[Dict[str, 'torch.Tensor']],
                return_pooled_features: bool=False) -> 'torch.Tensor':
        """This class is not a complete model.
        Use subclasses like ImageClassifier or TripletDistanceLearner or create new
        subclass."""
        raise NotImplementedError

    @classmethod
    def from_config(cls, cfg: 'CfgNode') -> Dict:
        """Classmethod to create an instance based on the config.

        Check detectron configs mechanism.

        Parameters
        ----------
        cfg: CfgNode
            Config

        Returns
        -------
        dict
            Dict with the relevant kwargs. This dict can be consumed by the
            __init__ function.
        """
        backbone, pixel_mean, pixel_std = build_backbone(cfg)
        if cfg.MODEL.get('FEATURE_EXTRACTION', None) is None:
            raise KeyError('The config is missing the cfg.MODEL.FEATURE_EXTRACTION node. '
                           'This is most likely because the config was created for an older version of the package. '
                           'Try converting the config using the function '
                           '\'sap_computer_vision.modelling.base.adjust_model_configs_base_'
                           'architecture_to_feature_extraction_node\'.')
        kwargs_base = {
            "backbone": backbone,
            "pixel_mean": pixel_mean,
            "pixel_std": pixel_std,
            "intermediate_sizes": cfg.MODEL.FEATURE_EXTRACTION.INTERMEDIATE_SIZE,
            "dropout": cfg.MODEL.FEATURE_EXTRACTION.DROPOUT_FC,
            "pooling": cfg.MODEL.FEATURE_EXTRACTION.POOL_BACKBONE_FEATURES,
            "normalize_output": cfg.MODEL.FEATURE_EXTRACTION.NORMALIZE_OUTPUT,
            "out_dim": cfg.MODEL.FEATURE_EXTRACTION.PROJECTION_SIZE,
            "image_size": cfg.INPUT.FIXED_IMAGE_SIZE,
            "freeze_backbone": cfg.MODEL.FEATURE_EXTRACTION.FREEZE_BACKBONE
        }
        return kwargs_base

    @property
    def device(self):
        return self.pixel_mean.device

    def preprocess_image(self, batched_inputs: List[Dict[str, torch.Tensor]], image_key: str='image') -> 'ImageList':
        """
        Normalize, pad and batch the input images.

        Parameters
        ----------
        batched_inputs: list of dicts
            List of input dicts
        image_key: str, optinal, default='image'
            Key of the images in the input dict

        Returns
        -------
        ImageList
            Returns instance of detectron2.ImageList
        """
        images = [x[image_key].to(self.device) for x in batched_inputs]
        images = [(x - self.pixel_mean) / self.pixel_std for x in images]
        images = ImageList.from_tensors(images, self.backbone.size_divisibility)
        return images

    def inference(self,
                  batched_inputs: List[Dict[str, torch.Tensor]],
                  return_pooled_features: bool=False,
                  image_key: str='image') -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
        """Forward step of the model.

        Parameters
        ----------
        batched_inputs: list of dicts
            Input batch
        return_pooled_features: bool, optinal, default=False
            If only the embeddings (False) or the embeddings and the
            pooled/unpooled backbone features should be returned.
            The backbone features can be used to visualize
            similarities as seen by the model between images.
            Check sap_computer_vision.utils.deep_similarity.

        Returns
        -------
        torch.Tensor or Tuple[torch.Tensor, torch.Tensor, torch.Tensor]
            Returns the embedding tensor and if return_pooled_features=True
            pooled and unpoold backbone features.
        """
        images = self.preprocess_image(batched_inputs, image_key)
        features = self.backbone(images.tensor)
        returns = []
        features = tuple(features[f] for f in self.used_backbone_feats)
        if self.pooling:

            if return_pooled_features:
                returns.append(features)
            features = tuple(torch.flatten(self.pooler(f), start_dim=1) for f in features)
            if return_pooled_features:
                returns.append(features)
        else:
            features = tuple((torch.flatten(f, start_dim=1) for f in features))
        features = torch.cat(features, 1)
        for i in range(self.projection_layers):
            l = getattr(self, f'projection_layer_{i+1}')
            features = l(features)
        features = self.out(features)
        if self.normalize_output:
            features = nn.functional.normalize(features, p=2.0, dim=1)
        if return_pooled_features:
            if not self.pooling:
                raise AttributeError('The model is initialized with `pooling=False`, '
                                     'therefore returning pooled features is not possible')
            returns.append(features)
            return returns[::-1]
        else:
            return features


def adjust_model_configs_base_architecture_to_feature_extraction_node(cfg: CfgNode):
    """Function to transform old img clf and triplet learner configs to new structure.

    Previously the architecture of the feature extraction part was defined in the nodes
    cfg.MODEL.IMAGE_CLASSIFICATION/cfg.MODEL.TRIPLET_DISTANCE_LEARNER.
    For more consistency most options were moved to the config node cfg.MODEL.FEATURE_EXTRACTION.
    """
    fe_node = cfg.MODEL.get('FEATURE_EXTRACTION', CfgNode({}))
    if cfg.MODEL.META_ARCHITECTURE == 'ImageClassifier':
        model_node =  cfg.MODEL.get('IMAGE_CLASSIFIER')
        defaults = {
            'PROJECTION_SIZE': model_node.NUM_CLASSES,
            'INTERMEDIATE_SIZE': 500,
            'DROPOUT_FC': 0.5,
            'IN_FEATURES': None,
            'NORMALIZE_OUTPUT': False,
            'POOL_BACKBONE_FEATURES': False,
        }
        model_node_values = {
            'NUM_CLASSES': None
        }

    elif cfg.MODEL.META_ARCHITECTURE == 'TripletDistanceLearner':
        model_node =  cfg.MODEL.get('TRIPLET_DISTANCE_LEARNER')
        defaults = {
            'PROJECTION_SIZE': 500,
            'INTERMEDIATE_SIZE': None,
            'DROPOUT_FC': 0.5,
            'IN_FEATURES': None,
            'NORMALIZE_OUTPUT': True,
            'POOL_BACKBONE_FEATURES': False,
            'FREEZE_BACKBONE': False,
        }
        model_node_values = {}
    else:
        return cfg

    for k, v in defaults.items():
        fe_node[k] = model_node.get(k, v)

    for k, v in model_node_values.items():
        model_node[k] = v

    cfg.MODEL['FEATURE_EXTRACTION'] = fe_node
    return cfg
