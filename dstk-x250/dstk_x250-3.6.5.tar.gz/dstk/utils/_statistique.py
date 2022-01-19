#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonctions de statistiques
^^^^^^^^^^^^^^^^^^^^^^^^^

Created on Tue Nov 24 12:32:10 2020

@author: Cyrile Delestre
"""

from typing import Optional, Union, List, Tuple

import numpy as np


def weighted_avg_and_std(
    x: np.ndarray,
    sample_weight: Optional[np.ndarray]=None,
    axis: Optional[Union[int, List[int], Tuple[int]]]=None,
    preserved_dim: bool=False
):
    """
    Retourne la moyenne de l'écart-type avec un poids sur chaque mesure.

    Parameters
    ----------
    x : np.ndarray
        variable aléatoire.
    sample_weight : Optional[np.ndarray] (=None)
        poids sur les samples. Doit avoir la même dimension que x un vecteur
        colonne.
    axis : Optional[Uniont[int, List[int], Tuple[int]]] (=None)
        dimension(s) de l'opération. Si None fait sur toutes les dimensions.
    preserved_dim : bool (=False)
        permet de signifier si le nombre dimensions de x sont préservées si
        axis est différent de None. False correspond au comportement standars
        de numpy.

    Returns
    -------
    mean : Union[np.ndarray, float]
        moyenne pondérée, scalaire si axis = None, sinon
        (n1 x ... x nq-1) si axis = i. Si preserved_dim 
        (n1 x ... x ni=1 x ... nq-1) si axis = i.
    std : Union[np.ndarray, float]
        écart-type pondéré, scalaire si axis = None, sinon
        (n1 x ... x nq) si axis = i. Si preserved_dim 
        (n1 x ... x ni=1 x ... nq-1) si axis = i.

    Notes
    -----
    Cette fonction retourne également la moyenne car elle en as besoin pour
    le calcul de la variance. Il s'agit également de la moyenne pondérée.
    """
    mean = np.average(
        a=x,
        weights=sample_weight,
        axis=axis
    )
    if axis:
        mean = np.expand_dims(mean, axis=axis)
    var = np.average(
        a=(x-mean)**2,
        weights=sample_weight,
        axis=axis
    )
    if preserved_dim and axis:
        var = np.expand_dims(var, axis=axis)
    else:
        mean = np.squeeze(mean, axis=axis)
    return mean, np.sqrt(var)

