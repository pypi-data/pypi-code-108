#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Méthodes utiles pour l'exploitation PyTorch

Created on Thu Oct 31 09:42:49 2019

@author: Cyrile Delestre
"""
from typing import Union, Optional, Tuple, List, Type, Dict, Any
from warnings import warn

import numpy as np
from pandas.core.frame import DataFrame

import torch

from dstk.utils import shape_list
from dstk.utils.deprecated import deprecated
from dstk.utils.errors import CheckError


def check_tensor(
        array: Union[torch.Tensor, np.ndarray, DataFrame, List, Tuple, int, float],
        dtype: Optional[Type]=None
    ):
    r"""
    Fonction vérifiant si le type de l'entrée est bien transformable en Tensor 
    PyTorch et, si c'est le cas, transformation de ce dernier en suivant le 
    type dtype. Si l'array n'est pas transformable, envoit d'une erreur de 
    type ErrorCheck.
    
    Parameters
    ----------
    array : Union[Tensor, np.ndarray, DataFrame, List, Tuple, int, float]
        checkage de l'array + conversion en Tensor.
    dtype : Optional[Type]
        cast vers un type PyTorch. Si None prend le type de l'array ou du 
        scalaire par défaut. Attention, type PyTorch (torch.int32, etc.)
    
    Returns
    -------
    tensor : Tensor
        array transformé en tensor au type dtype
    """
    if isinstance(array, torch.Tensor):
        return array if dtype is None else array.to(dtype)
    elif isinstance(array, np.ndarray):
        return (
            torch.from_numpy(array)
            if dtype is None
            else torch.from_numpy(array).to(dtype)
        )
    elif isinstance(array, DataFrame):
        return (
            torch.from_numpy(array.values)
            if dtype is None
            else torch.from_numpy(array.values).to(dtype)
        )
    elif isinstance(array, (list, tuple,)):
        return (
            torch.from_numpy(np.array(array))
            if dtype is None
            else torch.from_numpy(np.array(array)).to(dtype)
        )
    elif isinstance(array, (int, float, np.integer, np.floating,)):
        return (
            torch.Tensor(np.array([array]))
            if dtype is None
            else torch.Tensor(np.array([array])).to(dtype)
        )
    else:
        raise CheckError


def check_tensor_dict(data: Dict[str, Any], add_dim_batch: bool=False):
    r"""
    Fonction qui va transformer les éléments d'un dictionnaire en PyTorch 
    Tensor si c'est faisable.
    
    Parameters
    ----------
    data : Dict[str, Any]
        dictionnaire pouvant contenir ce que l'on souhaite.
    add_dim_batch : bool (=False)
        ajoute la dimension du batch si elle n'est pas présente.

    Returns
    -------
    data : Dict[str, Tensor]
        dictionnaire contenant des Tensor
    """
    def prepar_data(x):
        data_ = check_tensor(data[x])
        return data_.unsqueeze(0) if add_dim_batch else data_
    return {
        ii: prepar_data(ii)
        for ii in data 
        if isinstance(
            data[ii],
            (torch.Tensor, np.ndarray, list, tuple, DataFrame, int, float,
             np.integer, np.floating,)
        )
    }


@deprecated("Fonction plus utilisé, sera supprimée dans les MAJ à venir !")
def detach(array):
    r"""
    Fonction générique détachant les tensors du graph.
    
    Caution
    -------
    Fonction deprecated !
    
    Parameters
    ----------
    :array: liste/tuple de tensor, liste/tuple de liste/tuple de tensor,
        dictionnaire de tensor ou dictionnaire de liste/tuple de tensor.
    
    Returns
    -------
    Préservation de la structure de départ avec les tensors détachés du graph
    """
    if isinstance(array, (list, tuple)):
        if isinstance(array[0], torch.Tensor):
            res = []
            for aa in array:
                if aa.requires_grad:
                    res.append(aa.detach())
                else:
                    res.append(aa)
            if isinstance(array, tuple):
                return tuple(res)
            return res
        elif isinstance(array[0], (list, tuple)):
            if isinstance(array[0][0], torch.Tensor):
                res = []
                for aa in array:
                    res_int = []
                    for bb in aa:
                        if bb.requires_grad:
                            res_int.append(bb.detach())
                        else:
                            res_int.append(bb)
                    if isinstance(array[0], tuple):
                        res.append(tuple(res_int))
                    else:
                        res.append(res_int)
                if isinstance(array, tuple):
                    return tuple(res)
                return res
            else:
                raise TypeError(
                    "La fonction detach attend une liste/tuple de liste/tuple "
                    "de Tensor alors qu'il s'agit d'un type {} de {} de {}."
                    .format(
                        type(array),
                        type(array[0]),
                        type(array[0][0])
                    )
                )
        else:
            raise TypeError(
                "La fonction detach attend une liste/tuple de tensor ou une "
                "liste/tuple de liste/tuple alors qu'il s'agit d'un type {} "
                "de {}.".format(type(array), type(array))
            )
    elif isinstance(array, dict):
        items = list(array.items)
        if isinstance(items[0][0], (list, tuple)):
            if isinstance(items[0][0][0], torch.Tensor):
                res = []
                for key, aa in items:
                    res_int = []
                    for bb in aa:
                        if bb.requires_grad:
                            res_int.append(bb.detach())
                        else:
                            res_int.append(bb)
                    if isinstance(items[0][0], tuple):
                        res.append((key, tuple(res_int)))
                    else:
                        res.append((key, res_int))
                return dict(res)
            else:
                raise TypeError(
                    "La fonction detach attend un dictionnaire de liste/tuple "
                    "de Tensor alors qu'il s'agit d'un type {} de {} de {}."
                    .format(
                        type(array),
                        type(items[0][0]),
                        type(items[0][0][0])
                    )
                )
        elif isinstance(items[0][0], torch.Tensor):
            res = []
            for key, aa in items:
                if aa.requires_grad:
                    res.append((key, aa.detach()))
                else:
                    res.append((key, aa))
            return dict(res)
        else:
            raise TypeError(
                "La fonction detach attend un dictionnaire de Tensor alors "
                "qu'il s'agit d'un type {} de {}."
                .format(type(array), type(items[0][0]))
            )
    elif isinstance(array, torch.Tensor):
        if array.requires_grad:
            return array.detach()
        return array
    else:
        raise TypeError(
            "La fonction detach attend soit une liste/tuple, un dictionnaire "
            "ou un Tensor alors qu'il s'agit d'un type {}."
            .foramt(type(array))
        )


def collate_zeros_padding(
    sample: List[Dict[str, Union[torch.Tensor, np.ndarray]]],
    fields_series: List[Union[List, Tuple]],
    padding_value: float=0,
    torch_type: bool=True,
    batch_first: bool=True
):
    r"""
    Fonction de padding générique pour des séquences de différente longueur.
    
    Parameters
    ----------
    sample: List[Dict[str, Union[Tensor, np.ndarray]]]
        liste de dict des singletons composant le batch au format. Dans 
        un dictionnaire si size_field est défini utilise le size_field max
        de toute la list pour définir la taille max de l'array de la série. 
        Si  un array est plus grand il sera tronqué. Sinon prend le maximum 
        de  tous les arrays présente dans toutes les listes. Convertie ensuite 
        tous les champs en tensor. Exemple de sample :
            [{'a': np.array, 'b': np.array, 'siz_a': int, ...}, ...]
    fields_series : List[Union[List, Tuple]]
        liste de liste contenant le nom du champ de la série et 
        optionnellement le champ de la taille qui lui est associé. S'il n'y a 
        pas de champs associé à taille alors prend le maximum de la taille. 
        Par exemple avec l'exemple précédent :
            [['a', 'siz_a'], ['b']] ou  encore [['a', siz_a], ['b', None]]
    padding_value : float
        valeur des valeurs ajoutées. Par défaut 0.
    torch_type : bool
        retourne les vecteurs au format PyTorch (True) ou Numpy (False).
    batch_first : bool
        défini sur la première dimension est celle du batch (la seconde est 
        alors la série) ou l'inverse. Attention dans PyTorch par défaut dans 
        les RNN c'est l'inverse.
    
    Notes
    -----
    Il existe une fonction de zeros padding dans PyToch à surveiller. Mais 
    elle est pour le moment 10x plus lente que l'approche par completion d'un 
    array.
    
    Returns
    -------
    batch : Dict[str, Union[Tensor, np.ndarray]]
        dict au format :
            - {'a': tensor, 'b': tensor, 'siz_a': tensor, ...}
    """
    if len(sample) == 0:
        raise AttributeError(
            "L'ensemble des observations sample est vide : "
            f"len(sample) -> {len(sample)} !"
        )
    if not isinstance(sample[0], dict):
        raise AttributeError(
            "sample est une liste qui doit être composé de dictionnaire. Ce "
            f"n'est pas le cas : type(sample[0]) -> {type(sample[0])} !"
        )

    batch = {ff: None for ff in sample[0]}
    items_series = list(map(lambda x: x[0], fields_series))
    key_series = list(
        map(lambda x: x[1], filter(lambda y: len(y) == 2, fields_series))
    )

    for arg in batch:
        if arg in items_series:
            select_serie = list(
                filter(lambda x: x[0] == arg, fields_series)
            )[0]
            if len(select_serie) == 1 or select_serie[1] is None:
                key_len = None
                max_len = max(
                    sample,
                    key = lambda x: x[arg].shape[0]
                )[arg].shape[0]
            else:
                key_len = select_serie[1]
                max_len = max(
                    sample,
                    key = lambda x: x[key_len]
                )[key_len]

            obj_slice = None
            shape = sample[0][arg].shape
            if batch_first:
                global_shape = np.insert(shape, 0, len(sample))
                global_shape[1] = max_len
                if len(shape) == 1:
                    obj_slice = lambda ii, samp_len: np.s_[ii, :samp_len]
                elif len(shape) == 2:
                    obj_slice = lambda ii, samp_len: np.s_[ii, :samp_len, :]
            else:
                global_shape = np.insert(shape, 1, len(sample))
                global_shape[0] = max_len
                if len(shape) == 1:
                    obj_slice = lambda ii, samp_len: np.s_[:samp_len, ii]
                elif len(shape) == 2:
                    obj_slice = lambda ii, samp_len: np.s_[:samp_len, ii, :]
            if obj_slice is None:
                raise ValueError(
                    f"Dimension de série non supporté. La série {arg} est de "
                    "dimention len(sample[0][{arg}].shape) -> "
                    f"{len(sample[0][{arg}].shape)} !"
                )

            if isinstance(sample[0][arg], torch.Tensor):
                dtype = sample[0][arg].numpy().dtype
            else:
                dtype = sample[0][arg].dtype

            tensor = np.ones(global_shape, dtype=dtype)*padding_value

            for ii, samp in enumerate(sample):
                if key_len is None:
                    samp_len = samp[arg].shape[0]
                else:
                    samp_len = samp[key_len]
                tensor[obj_slice(ii, samp_len)] = samp[arg]
        else:
            if isinstance(sample[0][arg], (np.ndarray, torch.Tensor)):
                if isinstance(sample[0][arg], torch.Tensor):
                    dtype = sample[0][arg].numpy().dtype
                else:
                    dtype = sample[0][arg].dtype
                shape = np.insert(sample[0][arg].shape, 0, len(sample))
            elif isinstance(sample[0][arg], int):
                dtype = np.int32
                shape = (
                    (len(sample), 1,) if arg not in key_series
                    else (len(sample),)
                )
            elif isinstance(sample[0][arg], float):
                dtype = np.float32
                shape = (
                    (len(sample), 1,) if arg not in key_series
                    else (len(sample),)
                )
            else:
                raise ValueError(
                    f"Le type de l'argument {arg} est {type(sample[0][arg])} "
                    f"n'est pas pris en charge par l'implémentation. {arg} "
                    "doit être un ndarray, Tensor, int ou float."
                )

            if len(shape) == 1:
                obj_slice = lambda ii: np.s_[ii]
            elif len(shape) == 2:
                obj_slice = lambda ii: np.s_[ii, :]
            else:
                raise ValueError(
                    f"Dimension de série non supporté. La série {arg} est de "
                    f"dimention len(sample[0][{arg}].shape) -> "
                    f"{len(sample[0][arg].shape)} !"
                )

            tensor = np.zeros(shape, dtype=dtype)
            for ii, samp in enumerate(sample):
                tensor[obj_slice(ii)] = samp[arg]

        batch[arg] = torch.from_numpy(tensor) if torch_type else tensor
    return batch


def make_mask(
        in_features: int,
        out_features: int,
        n_channel: int,
        shift: int,
        kernel_size: int,
        repeat: Optional[Union[List, Tuple]]=None
) -> torch.BoolTensor:
    r"""
    Fonction de création de masque permettant de personaliser la topologie 
    des réseaux linéaires pour être autoregressif.
    
    Parameters
    ----------
    in_features : int
        taille en entré du réseau
    out_features : int
        taille en sortie du réseau
    n_channel : int
        nombre de neuronnes voyant les mêmes entrées
    shift : int
        décalage incrémentale sur chaques neuronnes
    kernel_size : int
        entrée contigue en entré du neuronne
    repeat : Optional[Union[List, Tuple]] (=None)
        tuple ou liste permettant de constituer les connexions (utile si 
        entrés multivariées).
    
    Returns
    -------
    mask : BoolTensor
        masque de dimension (out_feature x repeat[0]), 
        (in_features x repeat[1])
    
    Examples
    --------
    >>> import torch
    >>> from dstk.pytorch import make_mask
    >>> 
    >>> make_mask(6,6,1,0,2, repeat=(1,2)).type(torch.int8)
    tensor([[1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0]], dtype=torch.int8)
    >>> 
    >>> make_mask(6,6,2,2,2, repeat=(1,2)).type(torch.int8)
    tensor([[1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1]], dtype=torch.int8)
    """
    mask = torch.zeros(out_features, in_features, dtype=torch.bool)
    for ii in range(0, out_features, n_channel):
        ii_shift = int(ii/n_channel)*shift
        mask[ii:ii+n_channel, ii_shift:ii_shift+kernel_size] = True
    if repeat:
        return mask.repeat(repeat)
    return mask
