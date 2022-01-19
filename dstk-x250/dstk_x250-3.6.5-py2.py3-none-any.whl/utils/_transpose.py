#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transposition de dictionnaires
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Created on Wed Nov 25 11:37:41 2020

@author: Cyrile Delestre
"""

from typing import (List, Tuple, Union, Dict, Optional, Callable, Iterable,
                    NewType)

import numpy as np

TypeListOfDict = NewType(
    'TypeListOfDict',
    Union[
        List[Dict[str, Union[str, float, int]]],
        Tuple[Dict[str, Union[str, float, int]]]
    ]
)

def list_of_dict_2_dict_of_list(data: TypeListOfDict,
                                keys_trans: Optional[List[str]]=None,
                                type_trans: Callable=np.asarray):
    r"""
    Fonciton transposant un tuple ou une liste de dictionnaire en un 
    dictionnaire d'itérateur de type type_trans.
    
    Parameters
    ----------
    data : TypeListOfDict
        liste ou tuple de dictionnaire
    keys_trans : Optional[List[str]]
        clés des arguments du dico souhaité à être transposé, par défaut None 
        (toutes les clefs)
    type_trans : Callable
        type de la transposition, par défaut numpy array
    
    Examples
    --------
    >>> from dstk.utils import list_of_dict_2_dict_of_list as l2d
    
    >>> list_of_dict
        [{'a': 1, 'b': 4}, {'a': 2, 'b': 5}, {'a': 3, 'b': 6}]
    
    >>> l2d(list_of_dict, type_trans=list)
        {'a': [1, 2, 3], 'b': [4, 5, 6]}
    
    See also
    --------
    dict_of_list_2_list_of_dict
    """
    if not isinstance(data, (tuple, list)):
        raise ValueError(
            "data doit être du type tuple ou liste, et non de type "
            f"{type(data)}."
        )
    if keys_trans is None:
        keys_trans = data[0].keys()
    transpose = {
        key: type_trans(
            [dd[key] for dd in data]
        ) for key in keys_trans
    }
    return transpose

def dict_of_list_2_list_of_dict(data: Dict[str, Iterable],
                                keys_trans: Optional[List[str]]=None):
    r"""
    Fonction transposant un dictionnaire d'itérable en une liste de 
    dictionnaire.
    
    Parameters
    ----------
    data : Dict[str, Iterable]
        dictionnaire d'itérables que l'on souhaite transposer
    keys_trans : Optional[List[str]]
        clés des arguments du dico souhaité à être transposé, par défaut None 
        (toutes les clefs)
    
    Examples
    --------
    >>> from dstk.utils import dict_of_list_2_list_of_dict as d2l
    
    >>> dict_of_array
        {'a': array([1, 2, 3]), 'b': array([4, 5, 6])}
    
    >>> d2l(dict_of_array)
        [{'a': 1, 'b': 4}, {'a': 2, 'b': 5}, {'a': 3, 'b': 6}]
    
    See also
    --------
    dict_of_list_2_list_of_dict
    """
    if not isinstance(data, dict):
        raise ValueError(
            f"data doit être de type dict et non de type {type(data)}."
        )
    if keys_trans is None:
        keys_trans = data.keys()
    data = {kk: data[kk] for kk in keys_trans}
    kk, vv = zip(*data.items())
    transpose = [
        dict(zip(kk, ii)) for ii in zip(*vv)
    ]
    return transpose
