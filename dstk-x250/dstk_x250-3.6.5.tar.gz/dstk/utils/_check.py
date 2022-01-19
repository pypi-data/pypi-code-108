#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonctions de checkage
^^^^^^^^^^^^^^^^^^^^^

Created on Mon Nov 23 11:55:58 2020

@author: Cyrile Delestre
"""

from typing import Any, Union, Optional, List, Tuple

import pandas as pd

from dstk.utils.errors import NoConsistentError

def check_dataframe(X: Union[pd.DataFrame, Any],
                    columns_name: Optional[Union[str, list]]=None,
                    copy=False):
    """
    Foncton permettant de checker si la variable X est bien une DataFrame et
    optionnellement vérifie si la colonne ou la liste des colonnes de 
    columns_name est présente dans la DataFrame ou non. Cette fonction 
    permet de sortir également un copy de la DataFrame.
    
    Parameters
    ----------
    X : Union[pd.DataFrame, Any]
        variable à tester.
    columns_name : Optional[Union[str, list]]
        noms des colonnes à tester la présence dans a DataFrame X.
    copy: bool
        si True sort une copie de X.
    
    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> from dstk.utils import check_dataframe
    
    >>> array = np.array([1, 2, 3])
    >>> check_dataframe(array)
    AttributeError: L'argument d'entrée n'est pas une DataFrame mais une 
    <class 'numpy.ndarray'>.
    
    >>> df = pd.DataFrame({'a': [1, 2, 3], 'b': ['d', 'e', 'f']})
    >>> check_dataframe(df, ['a', 'c'])
    AttributeError: Les colonnes c ne sont pas présentes dans la DataFrame qui 
    a pour colonnes : a, b.
    """
    if not isinstance(X, pd.DataFrame):
        raise AttributeError(
            f"L'argument d'entrée n'est pas une DataFrame mais une {type(X)}."
        )
    if isinstance(columns_name, (list, tuple)):
        check = list(filter(lambda x: not x in X.columns, columns_name))
        if len(check) > 0:
            raise AttributeError(
                f"Les colonnes {', '.join(check)} ne sont pas présentes dans "
                "la DataFrame qui a pour colonnes : "
                f"{', '.join(X.columns.tolist())}."
            )
    elif isinstance(columns_name, str):
        if not columns_name in X.columns:
            raise AttributeError(
                f"La colonne {columns_name} n'est pas présente dans la "
                "DataFrame qui possède comme colonnes : "
                f"{', '.join(X.columns.tolist())}."
            )
    elif columns_name is not None:
        raise AttributeError(
            "columns_name doit être un string, un tuple ou une liste et non "
            f"de type {type(columns_name)}."
        )
    if copy:
        return X.copy()

def shape_list(l: Union[List[Any], Tuple[Any]]):
    r"""
    Fonction récurcive permettant de déterminer la dimension d'une liste ou 
    d'un tuple. Fonction retournant un résultat équivalent à shape du Numpy.
    
    Parameters
    ----------
    l : Union[List[Any], Tuple[Any]]
        liste ou typle de dimension inconue
    
    Returns
    -------
    shape : List[int]
        list contenant les dimensions de la liste ou du tuple.
    
    Examples
    --------
    >>> from dstk.utils import shape_list
    
    >>> my_list
    [[[3, 7], [1, 2], [2, 3]], [[7, 2], [3, 1], [0, 7]]]
    >>> shape_list(my_list)
    [2, 3, 2]
    
    >>> my_list_bis
    [[[3, 7], [1, 2], [2]], [[7, 2], [3, 1, 3], [0, 7]]]
    >>> shape_list(my_list_bis)
    NoConsistentError: La dimension 1 est non consistante.
    
    Notes
    -----
    La méthode vérifie la consistance de la liste. Si la liste n'est pas 
    consistante la fonction renvoit une erreur NoConsistentError.
    """
    if not isinstance(l, (list, tuple,)):
        return []
    if (isinstance(l[0], (list, tuple,))
            and len(set(map(lambda x: len(x), l))) > 1):
        raise NoConsistentError(
            "La dimension 0 est non consistante."
        )
    idx = 0
    return [len(l)] + _shape_list(l[0], idx)

def _shape_list(l: Union[List[Any], Tuple[Any]], idx: int):
    r"""
    Fonction privée. Permet de faire la récurcivité de shape_list tout en 
    indiquant la dimensions traité.
    
    Parametes :  Union[List[Any], Tuple[Any]]
        liste ou typle de dimension inconue
    idx : int
        indice de la dimensions pécédente
    """
    if not isinstance(l, (list, tuple,)):
        return []
    idx += 1
    if (isinstance(l[0], (list, tuple,))
            and len(set(map(lambda x: len(x), l))) > 1):
        raise NoConsistentError(
            f"La dimension {idx} est non consistante."
        )
    return [len(l)] + _shape_list(l[0], idx)
