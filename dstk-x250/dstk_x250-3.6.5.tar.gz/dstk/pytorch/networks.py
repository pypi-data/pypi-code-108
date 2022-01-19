#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modèles de réseaux MLP génériques utilisables pour PyTorch

Created on Mon Sep 16 14:42:57 2019

@author: Cyrile Delestre
"""
from typing import Optional, Callable, Union, Dict, Any, List, TypeVar, Tuple

import numpy as np

import torch
from torch.nn import (Module, Linear, LeakyReLU, ReLU, Dropout, Identity,
                      BatchNorm1d, LayerNorm, ModuleList, functional as F)

from dstk.pytorch import make_mask

TMLP = TypeVar('TMLP', bound='MLP')
TRNLL = TypeVar('TRNLL', bound='RisudualNonLinearLayer')

class MLP(Module):
    r"""
    Classe MLP de construction automatique en fonction du nombre de hidden
    layers et de la topologie des dimensions.
    
    Parameters
    ----------
    dim_in : int
        dimension d'entrée
    dim_out : int
        dimension de sortie
    dim_first_lay : int
        nombre de neronne de la première couche
    n_layers : int
        nombre de hidden layers
    embed_topo : str
        topologie des dimensions des hidden layers
            - linear: part de in_units et progresse linéairement vers 
            out_unist
            - bottleneck: part de in_units et progresse linéairement vers 
                inter_units puis progresse linéaiement vers out_units
        (par défaut 'linear')
    inter_units : int
        dimension intermédiaire pour l'option
        embed_topo = 'bottleneck', sinon inutile (par défaut 10)
    alpha : float
        coefficient de non-linéarité de la fonction d'activation LeakyReLU
        (par défaut 0.3)
    dropout_prob : float
        proportion de dropout en proba (par défaut 0 <= pas de dropout)
    batchnorm : bool
        utilise la batchnorm (par défaut True)
    dropout : bool
        utilise le dropout (par défaut True)
    batchnorm_last_layer : bool
        applique la batchnormalization sur la dernière couche (par défaut 
        True)
    activation_last_layer : Optional[Callable]
        permet d'envoyer une fonction d'activation sur la dernière couche 
        (logit). Si None, pas de fonction d'activation appliquée.
    dropout_last_layer : bool
        applique ou non le dropout sur la dernière couche (par défaut True)
    
    Returns
    -------
    res : Tensor
        La dimension de sortie est (None, out_units)
    """
    def __init__(
        self,
        dim_in: int,
        dim_out: int,
        dim_first_lay: int,
        n_layers: int,
        embed_topo: str='linear',
        inter_units: int=10,
        alpha: float=0.3,
        dropout_prob: float=0,
        batchnorm: bool=True,
        dropout: bool=True,
        batchnorm_last_layer: bool=True,
        activation_last_layer: Optional[Callable]=None,
        dropout_last_layer: bool=True
    ):
        assert embed_topo in ['linear', 'bottleneck'] \
            and dim_in > 0 \
            and dim_out > 0
        super(MLP, self).__init__()
        self.dim_in = dim_in
        self.dim_out = dim_out
        self.dim_first_lay = dim_first_lay
        self.n_layers = n_layers
        self.embed_topo = embed_topo
        self.inter_units = inter_units
        self.alpha = alpha
        self.dropout_prob = dropout_prob
        self.batchnorm = batchnorm
        self.dropout = dropout
        self.batchnorm_last_layer = batchnorm_last_layer
        self.activation_last_layer = activation_last_layer
        self.dropout_last_layer = dropout_last_layer
        self.build()

    def build(self) -> TMLP:
        r"""
        Fonction de construction du réseau de neurones.
        
        Warnings
        --------
        Pour Scikit-Learn, il faut que la fonction d'initialisation soit 
        différente de la fonction de construction.
        """
        if isinstance(self.activation_last_layer, bool):
            raise ValueError(
                "activation_last_layer est un booléen. Ce paramètre doit "
                "être une fonction ou None si aucune activation_last_layer "
                "ne doit être appliquée."
            )

        if self.n_layers > 1:
            if self.embed_topo == 'linear':
                    d_unite = (
                        (self.dim_first_lay-self.dim_out)/(self.n_layers-1)
                    )
                    units_by_lay = [
                        int(self.dim_first_lay-ii*d_unite)
                        for ii in range(self.n_layers)
                    ] 
            elif self.embed_topo == 'bottleneck':
                d_unite_1 = (
                    (self.dim_first_lay-self.inter_units)/
                    np.floor(self.n_layers/2)
                )
                units_dec = [
                    int(self.dim_first_lay-ii*d_unite_1)
                    for ii in range(int(np.floor(self.n_layers/2)))
                ]
                if self.n_layers == 2:
                    units_gro = [self.dim_out]
                else:
                    d_unite_2 = (
                        (self.inter_units-self.dim_out)/
                        np.ceil(self.n_layers/2-1)
                    )
                    units_gro = [
                        int(self.inter_units-ii*d_unite_2)
                        for ii in range(int(np.ceil(self.n_layers/2)))
                    ]
                units_by_lay = units_dec+units_gro
            else:
                raise AttributeError(
                    "Erreur embed_topo not in ['linear', 'bottleneck']"
                )
            units_in = [self.dim_in]+units_by_lay[:-1]
            units_out = units_by_lay
        else:
            units_in = [self.dim_in]
            units_out = [self.dim_out]
        layers = []
        for ii, nn in enumerate(zip(units_in, units_out)):
            n_in, n_out = nn
            layers.append(
                Linear(
                    in_features = n_in,
                    out_features = n_out,
                    bias = (
                        not self.batchnorm 
                        or (ii == self.n_layers-1 
                            and not self.batchnorm_last_layer)
                    )
                )
            )
            if (
                (ii < self.n_layers-1 or self.batchnorm_last_layer)
                and self.batchnorm
            ):
                layers.append(BatchNorm1d(num_features=n_out))
            if ii < self.n_layers-1:
                layers.append(LeakyReLU(negative_slope=self.alpha))
            if (
                ii == self.n_layers-1 and
                self.activation_last_layer is not None
            ):
                layers.append(self.activation_last_layer)
            if (
                (ii < self.n_layers-1 or self.dropout_last_layer)
                and self.dropout
            ):
                layers.append(Dropout(p=self.dropout_prob))
        self.layers = ModuleList(layers)
        return self

    def forward(self, inputs: torch.Tensor, **kargs) -> torch.Tensor:
        r"""
        Fonction d'appel du MLP
        
        Parameters
        ----------
        inputs : Tensor
            inputs de dimensions (batch_size, feat_size)
        
        Returns
        -------
        x_lay : Tensor
            sortie du MLP
        """
        x_lay = inputs
        for lay in self.layers:
            x_lay = lay(x_lay)
        return x_lay


class MaskedLinear(Linear):
    r"""
    Surcharge de la couche linéaire de PyTorch permettant de réaliser un 
    masque sur les poids afin de personaliser les connexions des neuronnes 
    composant la couche.
    Typiquement l'opération appliqué sera :
        input @ (mask*weight).T + bias
    Pour plus d'information sur la couche linéaire Linear de PyTorch, ce 
    référer à `la doc Linear`_.
    
    .. la doc Linear: https://pytorch.org/docs/stable/generated/torch.nn.Linear.html#torch.nn.Linear
    
    Parameters
    ----------
    in_features : int
        taille de l'entée de la couche linénaire
    out_features : int
        taille de la sortie de la couche linéaire
    bias : bool (=True)
        application d'un biais à la couche (True) ou non (False)
    """
    def __init__(self, in_features: int, out_features: int, bias: bool=True):
        super().__init__(
            in_features=in_features,
            out_features=out_features,
            bias=bias
        )
        self.register_buffer(
            'mask',
            torch.ones(out_features, in_features, dtype=torch.bool)
        )

    def set_mask(self, mask: Union[torch.BoolTensor, np.ndarray]) -> None:
        r"""
        Application d'un masque afin de personnaliser les connexions.
        
        Parameters
        ----------
        mask : Union[torch.BoolTensor, np.ndarray]
            Masque (out_features x in_features) qui doit être un numpy array 
            ou un tensor Booléen. 
        """
        if isinstance(mask, np.ndarray):
            mask = torch.from_numpy(mask.astype(np.bool))
        self.mask.data.copy_(mask)
        return self

    def forward(self, input: torch.Tensor, **kargs) -> torch.Tensor:
        return F.linear(input, self.mask*self.weight, self.bias)


class MaskedFeedForward(Module):
    r"""
    Couche non liénaire masqué à 1 couche cachée, inspiré de la couche 
    FeedForward de la modélisation détection de multi-attention Transformer.
    
    Paramreters
    -----------
    in_features : int
        taille de l'entée de la couche
    latent_features : int
        taille de l'espace latent
    in_kernel_size : int
        entrée contigue en entré du neuronne
    latent_channel : int
        nombre de neuronnes voyant les mêmes entrées de l'espace latent
    shift : int
        décalage incrémentale sur chaques neuronnes
    repeat: Optional[Union[List, Tuple]]
        répétition du masque si modèle multié série
    dropout_prob : float (=0.3)
        probabilité de dropout des différentes étages du réseau
    activation : Callable (=LeakyReLU(0.3))
        couche non linéaire d'activation
    """
    def __init__(
        self,
        in_features: int,
        latent_features: int,
        in_kernel_size: int,
        latent_channel: int,
        shift: int,
        repeat: Optional[Union[List, Tuple]]=None,
        dropout_prob: float=0.3,
        activation: Callable=LeakyReLU(0.3)
    ):
        super().__init__()
        self.in_features = in_features
        self.latent_features = latent_features
        self.in_kernel_size = in_kernel_size
        self.latent_channel = latent_channel
        self.shift = shift
        self.repeat = repeat
        self.dropout_prob = dropout_prob
        self.activation = activation
        self.build()

    def build(self) -> TRNLL:
        r"""
        Fonction de construction du réseau de neurones.
        
        Warnings
        --------
        Pour Scikit-Learn, il faut que la fonction d'initialisation soit 
        différente de la fonction de construction.
        """
        mask = make_mask(
            in_features=self.in_features,
            out_features=self.latent_features,
            n_channel=self.num_channel,
            shift=self.shift,
            repeat=self.repeat
        )
        self.linear_in = MaskedLinear(
            in_features=self.in_features,
            out_features=self.latent_features
        ).set_mask(mask)
        self.linear_out = MaskedLinear(
            in_features=self.latent_features,
            out_features=self.out_features
        ).set_mask(mask.T)
        self.norm_in = LayerNorm(self.in_features)
        self.norm_out = LayerNorm(self.out_features)
        self.dropout1 = Dropout(self.dropout_prob)
        self.dropout2 = Dropout(self.dropout_prob)
        return self

    def forward(self, input: torch.Tensor, **kargs) -> torch.Tensor:
        r"""
        Fonction d'appel du MaskedFeedForward
        
        Parameters
        ----------
        inputs : Tensor
            inputs de dimensions (batch_size, feat_size)
        
        Returns
        -------
        x : Tensor
            sortie du RisudualNonLinearLayer
        """
        input = self.norm_in(input)
        x = self.linear_out(
            self.dropout1(
                self.activation(
                    self.linear_in(input)
                )
            )
        )
        return self.norm_out(self.dropout2(x+input))

    def extra_repr(self) -> str:
        return (
            f"in_features={self.in_features}, "
            f"latent_features={self.latent_features}, "
            f"in_kernel_size={self.in_kernel_size}, "
            f"latent_channel={self.latent_channel}, "
            f"shift={self.shift}, "
            f"dropout_prob={self.dropout_prob}, "
            f"activation={self.activation}"
        )


class MaskedResidualLayer(Module):
    r"""
    Couche rédiuelle inspérée par le LSTM et utilisé notamment dans PixelNet 
    et WaveNet.
    
    Parameters
    ----------
    in_features : int
        taille de l'entée de la couche
    out_features : int
        taille de l'espace latent
    kernel_size : int
        entrée contigue en entré du neuronne
    shift : int
        décalage incrémentale sur chaques neuronnes
    repeat : Optional[Union[List, Tuple]]
        répétition du masque si modèle multié série
    dropout_prob : float (=0.3)
        probabilité de dropout des différentes étages du réseau
    """
    def __init__(self,
        in_features: int,
        out_features: int,
        kernel_size: int,
        shift: int,
        repeat: Optional[Union[List, Tuple]]=None,
        dropout_prob: float=0.3
    ):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.kernel_size = kernel_size
        self.shift = shift
        self.repeat = repeat
        self.dropout_prob = dropout_prob
        self.build()
    
    def build(self):
        r"""
        Fonction de construction du réseau de neurones.
        
        Warnings
        --------
        Pour Scikit-Learn, il faut que la fonction d'initialisation soit 
        différente de la fonction de construction.
        """
        mask = make_mask(
            in_features=self.in_features,
            out_features=self.out_features,
            n_channel=1,
            shift=self.shift,
            repeat=self.repeat
        )
        self.linear1 = MaskedLinear(
            in_features=self.in_features,
            out_features=self.latent_features
        ).set_mask(mask)
        self.linear2 = MaskedLinear(
            in_features=self.in_features,
            out_features=self.latent_features
        ).set_mask(mask)
        self.norm_in = LayerNorm(self.in_features)
        self.norm_out = LayerNorm(self.out_features)
        self.dropout1 = Dropout(self.dropout_prob)
        self.dropout2 = Dropout(self.dropout_prob)
        return self
    
    def forward(self, input: torch.Tensor, **kargs) -> torch.Tensor:
        r"""
        Fonction d'appel du MaskedResidualLayer
        
        Parameters
        ----------
        inputs : Tensor
            inputs de dimensions (batch_size, feat_size)
        
        Returns
        -------
        x : Tensor
            sortie du RisudualNonLinearLayer
        """
        input = self.norm_in(input)
        x = (
            self.dropout1(F.sigmoid(self.linear1(input))) 
            * self.dropout2(F.tanh(self.linear2(input)))
        )
        return self.norm_out(x + input)


class Autoregressive(Module):
    def __init__(
        self,
        dim_in: int,
        dim_out: int,
        connexion_layer: List[Dict[str, Any]]=[
            dict(n_layers=1, n_channel=1, shift=5, kernel_size=5),
            dict(n_layers=1, n_channel=1, shift=2, kernel_size=2),
            dict(n_layers=1, n_channel=1, shift=2, kernel_size=2)
        ],
        module_layer: Module=MaskedResidualLayer,
        last_activation: Module=Identity
    ):
        super().__init__()
        self.dim_in = dim_in
        self.dim_out = dim_out
        self.connexion_layer = connexion_layer
        self.module_layer = module_layer
        self.last_activation = last_activation
        self.build()
    
    def build(self):
        ...

    def forward(self, input: torch.Tensor, **kargs) -> torch.Tensor:
        ...
