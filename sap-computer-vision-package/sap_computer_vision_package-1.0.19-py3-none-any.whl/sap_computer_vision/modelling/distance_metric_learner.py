"""This module contains the meta architecture and loss functions for triplet distance learning."""
from typing import Callable, Dict, List, Tuple, Union
import logging

from detectron2.config import configurable, CfgNode
from detectron2.modeling import META_ARCH_REGISTRY

import torch
from torch import nn

from sap_computer_vision.data.triplet_sampling_utils import create_triplets_from_pk_sample, build_triplet_strategy

from .base import BaseModel


logger = logging.getLogger(__name__)


class SelectiveContrastiveTripletNCALoss(nn.Module):
    """'Selectively Contrastive Triplet Loss' as described
    in https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123590120.pdf.
    It is a standard Neighborhood Component Analysis Loss (NCA) with an
    additonal switch case. For triplet in wich the similarity between
    the anchor and the negative example is bigger than the similarity
    of the anchor and the positive example the loss is lambda*Similarity(a, n).
    Lambda is a tune able paramter.
    """
    def __init__(self,
                 lambda_: float=1.0,
                 swap: bool=False,
                 selective: bool=True,
                 reduction: Union[None, str]='mean',
                 dim: int=1,
                 eps: float=1e-08):
        """Create instance of Selectively Contrastive Triplet Loss'

        Parameters
        ----------
        lambda_: float, optinal, default=1.0
            Lambda-Parameter of the 'Selectively Contrastive Triplet Loss'
        swap: bool, optinal, default=True
            The distance swap is described in detail in the paper 'Learning
            shallow convolutional feature descriptors with triplet losses'
            by V. Balntas, E. Riba et al.
        selective: bool, optinal, default=True
            Enables/disables the additional condition from the
            'Selectively Contrastive Triplet Loss'. If False the loss
            is a standard NCA loss.
        reduction: None or str, default, optinal='mean'
            Specifies the reduction to apply to the output: None/'none' | 'mean' | 'sum'.
        dim: int, optinal, default=1
            'dim'-parameter of the nn.CosineSimilarity function.
        eps: float, optional, default=1e-08
            'eps'-parameter of the nn.CosineSimilarity function.
        """
        super().__init__()
        self.sim = nn.CosineSimilarity(dim=dim, eps=eps)
        self.swap = swap
        self.lambda_ = lambda_
        self.reduction = reduction
        self.selective = selective

    def forward(self, a: 'torch.Tensor', p: 'torch.Tensor', n: 'torch.Tensor') -> 'torch.Tensor':
        """Forward step of the step.

        Parameters
        ----------
        a: torch.Tensor
            Embedding of the anchors
        p: torch.Tensor
            Embedding of the positive examples
        n: torch.Tensor
            Embedding of the negative examples

        Returns
        -------
        torch.Tensor
            Loss
        """
        s_ap = self.sim(a, p)
        s_an = self.sim(a, n)
        if self.swap:
            s_pn = self.sim(p, n)
            mask = s_pn > s_an
            s_an[mask] = s_pn[mask]
        loss = torch.log(torch.exp(s_ap)+torch.exp(s_an)) - s_ap
        if self.selective:
            mask = s_an > s_ap
            loss[mask] = self.lambda_ * s_an[mask]
        if self.reduction == 'mean':
            return torch.mean(loss)
        elif self.reduction == 'sum':
            return torch.sum(loss)
        else:
            return loss


class SelectContrastiveTripletMarginLoss(nn.Module):
    """'Selectively Contrastive Triplet Loss' as described
    in https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123590120.pdf.
    It is a standard TripletMarginLoss with an
    additonal switch case. For triplet in wich the distance between
    the anchor and the negative example is smaller than the distance
    of the anchor and the positive example the loss is margin - dist(a, n).
    """
    def __init__(self, margin=0.1, p=2, swap=False, selective=True, reduction='mean'):
        """Triplet Margin Loss with addtion from "Hard negative examples are hard, but useful"
        Xuan et al.

        All parameters execept for the 'selective' parameter are identical to
        torch.nn.TripletMarginLoss. See its documentation for details.

        Paramters
        ---------
        margin: float, optinal, default=1.0
            Margin used in the loss.
        p: int, optional, default=2
            The norm degree for pairwise distance.
        swap: bool, optinal, default=True
            The distance swap is described in detail in the paper 'Learning
            shallow convolutional feature descriptors with triplet losses'
            by V. Balntas, E. Riba et al.
        selective: bool, optinal, default=True
            Enables/disables the additional condition from the
            'Selectively Contrastive Triplet Loss'. If False the loss
            is a standard NCA loss.
        reduction: None or str, default, optinal='mean'
            Specifies the reduction to apply to the output: None/'none' | 'mean' | 'sum'.
        """
        super().__init__()
        self.swap = swap
        self.p = p
        self.margin = margin
        self.reduction = reduction
        self.selective = selective

    def forward(self, a, p, n):
        """Forward step of the step.

        Parameters
        ----------
        a: torch.Tensor
            Embedding of the anchors
        p: torch.Tensor
            Embedding of the positive examples
        n: torch.Tensor
            Embedding of the negative examples

        Returns
        -------
        torch.Tensor
            Loss
        """
        d_ap = torch.norm(a-p, dim=1, p=self.p)
        d_an = torch.norm(a-n, dim=1, p=self.p)
        if self.swap:
            d_pn = torch.norm(p-n, dim=1, p=self.p)
            d_an = torch.where(d_pn < d_an, d_pn, d_an)
        loss = d_ap - d_an + self.margin
        if self.selective:
            alt_loss = self.margin - d_an
            loss = torch.where(d_ap > d_an, alt_loss, loss)
        loss = torch.max(torch.zeros_like(loss), loss)
        if self.reduction == 'mean':
            return torch.mean(loss)
        elif self.reduction == 'sum':
            return torch.sum(loss)
        else:
            return loss

class CircleLoss(nn.Module):
    """Implementation of CircleLoss taken from:
    https://github.com/TinyZeaMays/CircleLoss/blob/master/circle_loss.py
    with minor adaptation. CircleLoss is introduce in the paper
    "Circle Loss: A Unified Perspective of Pair Similarity Optimization"
    Sun et al.

    The basic idea is to build all possible triplets and weight them
    according to their "difficulty".
    """
    def __init__(self, m: float=0.5, gamma: float=256.) -> None:
        """
        Parameters
        ----------
        m: float, optinal, m=0.5
            Margin
        gamma: float, optinal, default=256.
            Scale factor, check paper for details.
        """
        super(CircleLoss, self).__init__()
        self.m = m
        self.gamma = gamma
        self.soft_plus = nn.Softplus()

    def forward(self, normed_feature: torch.Tensor, label: torch.Tensor) -> torch.Tensor:
        """Forward step of the loss.

        Parameters
        ----------
        normed_feature: torch.Tensor
            Embeddings
        label: torch.Tensor
            Class ids

        Return
        ------
        torch.Tensor
            Loss
        """
        inp_sp, inp_sn = self._convert_label_to_similarity(normed_feature, label)
        return self._loss_from_similarity_tensors(inp_sp, inp_sn)

    def _loss_from_similarity_tensors(self, sp: torch.Tensor, sn: torch.Tensor) -> torch.Tensor:
        ap = torch.clamp_min(- sp.detach() + 1 + self.m, min=0.)
        an = torch.clamp_min(sn.detach() + self.m, min=0.)

        delta_p = 1 - self.m
        delta_n = self.m

        logit_p = - ap * (sp - delta_p) * self.gamma
        logit_n = an * (sn - delta_n) * self.gamma

        loss = self.soft_plus(torch.logsumexp(logit_n, dim=0) + torch.logsumexp(logit_p, dim=0))
        return loss

    @staticmethod
    def _convert_label_to_similarity(normed_feature: torch.Tensor, label: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        similarity_matrix = normed_feature @ normed_feature.transpose(1, 0)
        label_matrix = label.unsqueeze(1) == label.unsqueeze(0)

        positive_matrix = label_matrix.triu(diagonal=1)
        negative_matrix = label_matrix.logical_not().triu(diagonal=1)

        similarity_matrix = similarity_matrix.view(-1)
        positive_matrix = positive_matrix.view(-1)
        negative_matrix = negative_matrix.view(-1)
        return similarity_matrix[positive_matrix], similarity_matrix[negative_matrix]


@META_ARCH_REGISTRY.register()
class TripletDistanceLearner(BaseModel):
    """Model for distance metric learning using triplets.

    The model architecture is taken from sap_computer_vision.modelling.base.BaseModel.
    The BaseModel is extended to support different loss functions and different sampling
    mechanisms/strategies for triples. Check sap_computer_vision.data.samplers of
    sampler options.
    """
    @configurable
    def __init__(self,
                 *,
                 backbone: 'nn.Module',
                 loss: Callable,
                 out_dim: Union[None, int]=None,
                 dropout: Union[None, float]=0.5,
                 pixel_mean: 'torch.Tensor',
                 pixel_std: 'torch.Tensor',
                 image_size: Union[None, int, Tuple[int, int]]=None,
                 intermediate_sizes: Union[None, List[str]]=None,
                 input_feats: Union[None, List[str]]=None,
                 triplet_strategy: Union[None, Tuple[str, str]]=None,
                 pooling: Union[bool, str]=True,
                 normalize_output: bool=True,
                 freeze_backbone: bool=False,
                 dist_norm: float=2.,
                 activation_projection_layer: Union[str, None]='ReLU'):
        """Create model instances.

        Parameters not documented here are documented for the BaseModel.

        Parameters
        ----------
        loss: nn.Module
            Loss function.
        out_dim: int or None
            Dimensionality of the feature vectors.
            If None the last layer is nn.Identity.
        triplet_strategy: None or Tuple(str/float, str/float), optional, defaul=None
            When using PKSampler the triplets are created within the model.
            If the used sampler already creates triplets the strategy should
            be None. The strategy should also be None when using CircleLoss
            (CircleLoss expects PKSampler, but the loss function creates the
            triplets). To specify a triplet (pos_strat, neg_strat) is expected.
            Options are 'rand'/'min'/'max' or a float between 0 and 1.
            - None: No stragty.
            - rand: random
            - min: minimal distance to the anchor
            - max: maximal distance to the anchor
            - float: loc of triplet_sampling_utils.SkedNormalSampler
        dist_norm: float, optinal, default=2.
            The norm degree for pairwise distance calculated for
            most triplet strategies.
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
        self.criterion = loss
        self.dist_norm = dist_norm
        self.triplet_strategy = self.build_triplet_strategy(triplet_strategy, self.criterion)


    @staticmethod
    def build_triplet_strategy(strategy: Union[None, Tuple[Union[str, float], Union[str, float]]],
                               criterion: Union[None, 'nn.Module']=None) -> Tuple[Union[str, Callable], Union[str, Callable]]:
        """Function used to check triplet strategy and create callable if needed.

        If strategy is not None and and criterion is not Circle loss,
        sap_computer_vision.data.triplet_sampling_utils.build_triplet_strategy is called.


        Parameters
        ----------
        strategy
            Strategy for triplet sampling.
            Check sap_computer_vision.data.triplet_sampling_utils.build_triplet_strategy for details.

        Returns
        -------
        Tuple(str/callable, str/callable)
            Tuple (pos_strat, neg_strat).
        """
        if strategy is None or isinstance(criterion, CircleLoss):
            if not (isinstance(strategy, str) and strategy.lower() == 'none') and strategy is not None:
                logger.warning('When using CircleLoss no triplet strategy is used!')
            return None
        return build_triplet_strategy(strategy)

    @classmethod
    def from_config(cls, cfg: CfgNode) -> Dict:
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
        loss, dist_norm = cls.build_loss(cfg)
        kwargs_clf = {
            "triplet_strategy": cfg.MODEL.TRIPLET_DISTANCE_LEARNER.TRIPLET_STRATEGY,
            "dist_norm": dist_norm,
            "loss": loss
        }
        return {**kwargs_base, **kwargs_clf}

    @staticmethod
    def build_loss(cfg: CfgNode, name: Union[None, str]=None) -> 'nn.Module':
        """Build loss functions

        Parameters
        ----------
        cfg: CfgNode
            Configuration
        name: str or None, optinal,
            Name of the loss available options are:
                - MARGIN_LOSS
                - NCA_LOSS
                - CIRCLE_LOSS
            If None cfg.MODEL.TRIPLET_DISTANCE_LEARNER.LOSS is used.

        Returns
        -------
        nn.Module
            Loss function
        """
        if name is None:
            name = cfg.MODEL.TRIPLET_DISTANCE_LEARNER.LOSS.lower()
        if name.upper() == 'CIRCLE_LOSS':
            if cfg.DATALOADER.SAMPLER_TRAIN != 'PKSampler':
                raise ValueError('`CIRCLE_LOSS` can only be used wiht `PKSampler` as the sampler for training.')
            criterion = CircleLoss(m=cfg.MODEL.TRIPLET_DISTANCE_LEARNER.CIRCLE_LOSS.MARGIN,
                                   gamma=cfg.MODEL.TRIPLET_DISTANCE_LEARNER.CIRCLE_LOSS.GAMMA)
            dist_norm = None
        elif name.upper() == 'MARGIN_LOSS':
            kwargs = {
                'margin': cfg.MODEL.TRIPLET_DISTANCE_LEARNER.MARGIN_LOSS.MARGIN,
                'p': cfg.MODEL.TRIPLET_DISTANCE_LEARNER.MARGIN_LOSS.NORM,
                'swap': cfg.MODEL.TRIPLET_DISTANCE_LEARNER.MARGIN_LOSS.SWAP,
                'reduction': 'mean'
            }
            if cfg.MODEL.TRIPLET_DISTANCE_LEARNER.MARGIN_LOSS.SELECTIVE:
                criterion = SelectContrastiveTripletMarginLoss(selective=True, **kwargs)
            else:
                criterion = nn.TripletMarginLoss(**kwargs)
            dist_norm = kwargs['p']
        elif name.upper() == 'NCA_LOSS':
            kwargs = {
                'lambda_': cfg.MODEL.TRIPLET_DISTANCE_LEARNER.NCA_LOSS.LAMBDA,
                'selective': cfg.MODEL.TRIPLET_DISTANCE_LEARNER.NCA_LOSS.SELECTIVE,
                'swap': cfg.MODEL.TRIPLET_DISTANCE_LEARNER.NCA_LOSS.SWAP
            }
            criterion = SelectiveContrastiveTripletNCALoss(dim=1, eps=1e-08, reduction='mean', **kwargs)
            dist_norm = 'cosine'
        else:
            raise ValueError(f'{name} is not a supported loss function.')
        return criterion, dist_norm

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
            if isinstance(self.criterion,CircleLoss):
                normalized_features = self.inference(batched_inputs)
                labels = torch.tensor([i['class_id'] for i in batched_inputs], dtype=torch.long).to(self.device)
                return self.criterion(normalized_features, labels)
            else:
                anchors, pos, neg = self.forward_for_triplets(batched_inputs)
                return self.criterion(anchors, pos, neg)
        else:
            return self.inference(batched_inputs, return_pooled_features=return_pooled_features)

    def forward_for_triplets(self, batched_inputs: List[Dict[str, 'torch.Tensor']]) -> Tuple['torch.Tensor', 'torch.Tensor', 'torch.Tensor']:
        """Forward step during Training if loss is not CircleLoss.
        The input data are triplets or triplets have to be sampled from the batch.

        Parameters
        ----------
        batched_inputs: list of dicts
            Input batch

        Returns
        -------
        Tuple[torch.Tensor, torch.Tensor, torch.Tensor]
            Returns embeddings for (anchors, positive examples, negative examples).
        """
        if self.triplet_strategy is None:  # Inpute is expected to already contain triplet dicts
            anchor = self.inference([trip['anchor'] for trip in batched_inputs])
            pos = self.inference([trip['pos'] for trip in batched_inputs])
            neg = self.inference([trip['neg'] for trip in batched_inputs])
            return anchor, pos, neg
        else:
            try:
                labels = torch.tensor([i['class_id'] for i in batched_inputs], dtype=torch.long).to(self.device)
            except KeyError as err:
                raise KeyError('`batched_input` has no key `class_id`. This is either because a dataset without labels or with triplets was used as the train dataset. '
                               'To train with a dataset of triplets set `MODEL.TRIPLET_DISTANCE_LEARNER.TRIPLET_STRATEGY=EXTERNAL`.') from err

            fw_results = self.inference(batched_inputs)
            a, p, n = create_triplets_from_pk_sample(fw_results,
                                                     labels,
                                                     strategy_pos=self.triplet_strategy[0],
                                                     strategy_neg=self.triplet_strategy[1],
                                                     dist_norm=self.dist_norm,
                                                     anchor_pos_combinations_unique=getattr(self.criterion, 'swap', False))
            return fw_results[a], fw_results[p], fw_results[n]
