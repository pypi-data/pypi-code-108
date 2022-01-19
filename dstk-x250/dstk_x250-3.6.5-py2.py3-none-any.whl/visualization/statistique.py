#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonctions ou classes utiles pour le la visualisation et l'analyse.

Created on Tue Apr 14 22:44:11 2020

@author: Cyrile Delestre
"""

from typing import Callable, Optional, NewType
from math import erf

import numpy as np

TypeCDF = NewType(
    'TypeCDF',
    Callable[[np.ndarray, Optional[float], Optional[float]], np.ndarray]
)

@np.vectorize
def cdf_normal(x: np.ndarray, mean: float=0, std: float=1):
    r"""
    Fonction vectorisée permettant de calculer la CDF de la loi Normale.
    
    Parameters
    ----------
    x : ndarray
        points d'évaluation de la CDF.
    mean : float
        moyenne
    std : float
        écart-type
    
    See also
    --------
    cdf_rayleigh, kolmogorov_smirnov_test
    """
    return 1/2*(1+erf((x-mean)/(std*np.sqrt(2))))

def cdf_rayleigh(x: np.ndarray, mean: float=1, std: None=None):
    r"""
    Fonction vectorisée permettant de calculer la CDF de la loi Rayleigh.
    
    Parameters
    ----------
    x : ndarray
        points d'évaluation de la CDF.
    mean : float
        moyenne
    std : None
        pour être ISO avec la fonction 
        :func:`~dstk.visualization.statistique.cdf_normal` (inutilisé).
    
    See also
    --------
    cdf_normal, kolmogorov_smirnov_test
    """
    if mean <= 0:
        raise AttributeError(
            "La moyenne de la loi de Rayleigh est strictement positive."
        )
    x_ = np.zeros_like(x)
    filt = x >= 0
    sig = mean*(np.pi/2)**2
    x_[filt] = 1 - np.exp(-x[filt]**2/(2*sig**2))
    return x_

def kolmogorov_smirnov_test(x: np.ndarray,
                            cdf: TypeCDF,
                            mean: Optional[float],
                            std: Optional[float],
                            **kargs):
    r"""
    Fonction permettant de calculer l'écart entre deux CDF du test de 
    Kolmogorow-Smirnov.
    
    Parameters
    ----------
    x : np.ndarray
        variable aléatoire suivant une loi inconnue.
    cdf : TypeCDF
        fonction de CDF continue.
    mean : Optional[float]
        moyenne estimée de la variable x.
    std : Optional[float]
        écrat-type estimé de la variable x.
    **kargs :
        arguments pour la fonction histogram de Numpy.
    
    Returns
    -------
    Ecart de Kolmogorow-Smirnov.
    
    Notes
    -----
    La fonction cdf doit avoir le format :
        cdf(x: np.array, mean: float, std: float)
    Les arguments mean et std sont juste des noms en référence à la loie 
    normale, elles peuvent représentrer d'autres carastéristiques 
    statistiques. Si la cdf à besoins de plus de 2 caractéristiques pour être 
    calculé, cette fonction ne fonctionnera pas.
    
    .. todo:: Faire une méthode qui permettrait d'avoir autant de 
        caractéristiques statistiques souhaité. (attention a RocAnalyser !)
    
    See also
    --------
    cdf_normal, cdf_rayleigh
    """
    if 'density' in kargs.keys():
        del kargs['density']
    hist, bin_edges = np.histogram(x, density=False, **kargs)
    cum_hist = np.cumsum(hist)/x.shape[0]
    theo = cdf(bin_edges[1:], mean=mean, std=std)
    return np.max(np.abs(theo-cum_hist))
