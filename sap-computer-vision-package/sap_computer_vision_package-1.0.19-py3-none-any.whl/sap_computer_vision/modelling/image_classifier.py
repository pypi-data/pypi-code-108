"""This module contains the meta architecture for image classification."""
from typing import Dict, List, Tuple, Union

from detectron2.config import configurable
from detectron2.modeling import META_ARCH_REGISTRY

import torch
from torch import nn

from .base import BaseModel


@META_ARCH_REGISTRY.register()
class ImageClassifier(BaseModel):
    """Model for image classification.

    The model architecture is taken from sap_computer_vision.modelling.base.BaseModel.
    Right now BCEWithLogitsLoss, CrossEntropyLoss and MultiLabelSoftMarginLoss
    are loss available.
    """

    @configurable
    def __init__(self,
                 *,
                 backbone: 'nn.Module',
                 pixel_mean: 'torch.Tensor',
                 pixel_std: 'torch.Tensor',
                 out_dim: Union[None, int]=None,
                 n_classes: Union[None, int]=None,
                 dropout: Union[None, float]=0.5,
                 image_size: Union[None, int, Tuple[int, int]]=None,
                 intermediate_sizes: Union[None, int, List[int]]=None,
                 input_feats: Union[None, List[str]]=None,
                 pooling: Union[bool, str]=True,
                 multi_label: bool=False,
                 normalize_output: bool=False,
                 freeze_backbone: bool=False,
                 activation_projection_layer: Union[str, None]='ReLU'):
        """Create model instances.

        Parameters not documented here are documented for the BaseModel.

        Parameters
        ----------
        loss: nn.Module
            Loss function.
        n_classes: int or None
            Nubmer of classes/labels
        multi_label: bool, optional, default=False
            Multi label use cases.
            Beware: This should be seen as a placeholder, since multi label problems
            are not yet supported by this repos
        """
        super().__init__(
                 backbone=backbone,
                 out_dim=out_dim,
                 intermediate_sizes=intermediate_sizes,
                 dropout=dropout,
                 image_size=image_size,
                 pixel_mean=pixel_mean,
                 pixel_std=pixel_std,
                 input_feats=input_feats,
                 pooling=pooling,
                 normalize_output=normalize_output,
                 freeze_backbone=freeze_backbone,
                 activation_projection_layer=activation_projection_layer)
        self.clf_layer = nn.Identity() if n_classes is None else nn.Linear(self.out_dim, n_classes)
        self.softmax = nn.Softmax(dim=1)
        if multi_label:
            self.multi_label = True
            self.criterion = nn.MultiLabelSoftMarginLoss()
        elif out_dim == 2:
            self.multi_label = False
            self.criterion = nn.BCEWithLogitsLoss()
        else:
            self.multi_label = False
            self.criterion = nn.CrossEntropyLoss()

    @classmethod
    def from_config(cls, cfg) -> Dict:
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
        kwargs_base = BaseModel.from_config(cfg)
        kwargs_clf = {
            "n_classes": cfg.MODEL.IMAGE_CLASSIFIER.NUM_CLASSES,
            "multi_label": cfg.MODEL.IMAGE_CLASSIFIER.MULTI_LABEL
        }
        return {**kwargs_base, **kwargs_clf}

    def forward(self,
                batched_inputs: List[Dict[str, 'torch.Tensor']],
                return_pooled_features: bool=False) -> 'torch.Tensor':
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
        if self.training:
            fw_results = self.inference(batched_inputs, return_pooled_features=False)
            fw_results = self.clf_layer(fw_results)
            if self.multi_label:
                raise NotImplementedError
            labels = torch.tensor([i['class_id'] for i in batched_inputs], dtype=torch.long).to(self.device)
            return self.criterion(fw_results, labels)
        if return_pooled_features:
            fw_results, pooled, unpool = self.inference(batched_inputs,
                                                        return_pooled_features=return_pooled_features)
            return self.softmax(self.clf_layer(fw_results)), pooled, unpool
        return self.softmax(self.clf_layer(self.inference(batched_inputs)))
