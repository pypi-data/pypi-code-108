#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe et fonction des chunkers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Created on Mon Nov 23 09:38:09 2020

@author: Cyrile Delestre
"""

from dataclasses import dataclass
from typing import Any, Union, List
from math import ceil, floor

import pandas as pd
import numpy as np


@dataclass
class Chunker:
    r"""
    Classe permettant de tronçonner une liste data d'objets en N paquets de 
    taille size.
    
    Parameters
    ----------
    data : Union[List[Any], np.ndarray, pd.DataFrame]
        array-like ou liste d'éléments
    size : int
        taille d'un tronçon
    drop_remainder : bool
        élimine le dernier tronçon si ce dernier n'est pas de taille size (si 
        len(data) n'est pas divisible par size).
    
    Notes
    -----
    Convient si la donnée ne prend pas trop de place sur la RAM sinon utiliser 
    la fonction "chuncker".
    
    Examples
    --------
    >>> from dstk.utils import Chunker
    >>> 
    >>> chunk = Chunker(list(range(1000)), 10)
    >>> len(chunk)
    100
    >>> chunk[5]
    [50, 51, 52, 53, 54, 55, 56, 57, 58, 59]
    >>> chunk[100]
    IndexError: Index out of band, l'index doit être compris entre 0 et 99.
    
    See also
    --------
    chuncker
    """
    data: Union[List[Any], np.ndarray, pd.DataFrame]
    size: int
    drop_remainder: bool=False
    def __post_init__(self):
        if not isinstance(self.data, (list, np.ndarray, pd.DataFrame)):
            raise AttributeError(
                "data doit être un array-like (list, NumPy array ou "
                f"DataFrame) et non de type {type(self.data)}."
            )
        self.pandas = False
        if isinstance(self.data, pd.DataFrame):
            self.pandas = True
    
    def __len__(self):
        if self.drop_remainder:
            return floor(len(self.data)/self.size)
        else:
            return ceil(len(self.data)/self.size)

    def __getitem__(self, idx):
        if idx > self.__len__()-1:
            raise IndexError(
                "Index out of band, l'index doit être compris entre 0 et "
                f"{self.__len__()-1}."
            )
        if idx < -self.__len__()+1:
            raise IndexError(
                "Index out of band, l'index doit être compris entre -1 et "
                f"{-self.__len__()+1}."
            )
        return (
            self.data[
                idx*self.size:
                idx*self.size+self.size if idx != -1 else len(self.data)
            ]
            if not self.pandas else
            self.data.iloc[
                idx*self.size:
                idx*self.size+self.size if idx != -1 else len(self.data)
            ]
        )


def chunker(
    data: Union[List[Any], np.ndarray, pd.DataFrame],
    size: int,
    drop_remainder: bool=False
):
    r"""
    Chunker pour de grosses volumétries. Génère un générateur consommant  
    aucun espace RAM supplémentaire (par rapport à la data source).
    
    Parameters
    ----------
    data : Union[List[Any], np.ndarray, pd.DataFrame]
        array-like ou liste d'éléments
    size : int
        taille d'un tronçon
    drop_remainder : bool
        élimine le dernier tronçon si ce dernier n'est pas de taille size (si 
        len(data) n'est pas divisible par size).
    
    Notes
    -----
    Si la volumétrie le permet, utiliser plutôt la classe Chunker qui facilite 
    la manipulation du chunker.
    
    Examples
    --------
    >>> from dstk.utils import chunker
    >>> 
    >>> chunk = chunker(range(1000), 10)
    >>> next(chunk)
    range(0, 10)
    >>> next(chunck)
    range(10, 20)
    >>> ...
    >>> next(chunck)
    StopIteration
    
    See also
    --------
    Chuncker
    """
    if isinstance(data, (list, np.ndarray)):
        if drop_remainder:
            for ii in range(0, len(data)-(len(data)%size), size):
                yield data[ii:ii+size]
        else:
            for ii in range(0, len(data), size):
                yield data[ii:ii+size]
    elif isinstance(data, pd.DataFrame):
        if drop_remainder:
            for ii in range(0, len(data)-(len(data)%size), size):
                yield data.iloc[ii:ii+size]
        else:
            for ii in range(0, len(data), size):
                yield data.iloc[ii:ii+size]
    else:
        raise AttributeError(
            "data doit être un array-like (list, NumPy array ou DataFrame) "
            f"et non de type {type(data)}."
        )
