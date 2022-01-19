#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de métriques utiles pour les approches online

Created on Wed Nov  6 11:26:53 2019

@author: Cyrile.Delestre
"""
import warnings
from typing import (Union, Iterable, Dict, Any, Optional, NewType, List,
                    Callable)
from functools import wraps

import numpy as np
from pandas import DataFrame, Series
from sklearn.metrics import (mean_absolute_error, median_absolute_error,
                             mean_squared_error, accuracy_score, roc_auc_score,
                             precision_score, precision_recall_fscore_support)

from ._base import BaseEnvironnement

PyTorchEstimators = NewType('PyTorchEstimators', BaseEnvironnement)

def mean_absolute_error_online(estimator: PyTorchEstimators,
                               X: Iterable,
                               y_true: Iterable,
                               kargs_fit: Dict[str, Any],
                               gap: int=0,
                               idx_skip: Optional[Union[np.ndarray,
                                                        List[int]]]=None,
                               **kargs):
    r"""
    Fonction mean_absolute_error appliquée au contexte online. Voici la 
    documentation Scikit-Learn :
        `mean_absolute_error`_
    
    .. _mean_absolute_error: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_error.html
    
    Parameters
    ----------
    estimator : PyTorchEstimators
        objet estimator de type regressor
    X : Iterable
        observations
    y_true : Iterable
        targets associées aux observations X
    kargs_fit : Dict[str, Any]
        dictionnaire des arguments nécéssaires au fit
    gap : int
        Permet de définir un gap entre l'apprentissage du modèle et la 
        prédiction. Par défaut 0, aucun gap. Dans la pratique le gap est à 
        minima égal à l'horizon de prédiction.
    idx_skip : Optional[Union[np.ndarray, List[int]]]
        indices des observation à exclure. Permet de limiter l'effet des black 
        swan pour cetain type de série.
    **kargs :
        paramètres associés à la fonction Scikit-Learn (voir la doc 
        Scikit-Learn).
    """
    check_estimator(
        estimator=estimator,
        estimator_type='regressor',
        fun_score='mean_absolute_error_online'
    )
    y_pred = estimator.fit_online(
        X,
        predict = True,
        gap = gap,
        **kargs_fit
    )
    y_true, y_pred = skip_obs(y_true[gap:], y_pred, idx_skip, gap)
    return apply_metric_error(
        mean_absolute_error,
        y_true,
        y_pred,
        **kargs
    )

def median_absolute_error_online(estimator: PyTorchEstimators,
                                 X: Iterable,
                                 y_true: Iterable,
                                 kargs_fit: Dict[str, Any],
                                 gap: int=0,
                                 idx_skip: Optional[Union[np.ndarray,
                                                          List[int]]]=None,
                                 **kargs):
    r"""
    Fonction median_absolute_error appliquée au contexte online. Voici la 
    documentation Scikit-Learn :
        `median_absolute_error`_
    
    .. _median_absolute_error: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.median_absolute_error.html?highlight=median%20absolute
    
    Parameters
    ----------
    estimator : PyTorchEstimators
        objet estimator de type regressor
    X : Iterable
        observations
    y_true : Iterable
        targets associées aux observations X
    kargs_fit : Dict[str, Any]
        dictionnaire des arguments nécéssaires au fit
    gap : int
        Permet de définir un gap entre l'apprentissage du modèle et la 
        prédiction. Par défaut 0, aucun gap. Dans la pratique le gap est à 
        minima égal à l'horizon de prédiction.
    idx_skip : Optional[Union[np.ndarray, List[int]]]
        indices des observation à exclure. Permet de limiter l'effet des black 
        swan pour cetain type de série.
    **kargs :
        paramètres associés à la fonction Scikit-Learn (voir la doc 
        Scikit-Learn).
    """
    check_estimator(
        estimator=estimator,
        estimator_type='regressor',
        fun_score='median_absolute_error_online'
    )
    y_pred = estimator.fit_online(
        X,
        predict=True,
        gap=gap,
        **kargs_fit
    )
    y_true, y_pred = skip_obs(y_true[gap:], y_pred, idx_skip, gap)
    return apply_metric_error(
        median_absolute_error,
        y_true,
        y_pred,
        **kargs
    )

def mean_squared_error_online(estimator: PyTorchEstimators,
                              X: Iterable,
                              y_true: Iterable,
                              kargs_fit: Dict[str, Any],
                              gap: int=0,
                              idx_skip: Optional[Union[np.ndarray,
                                                       List[int]]]=None,
                              **kargs):
    r"""
    Fonction mean_squared_error appliquée au contexte online. Voici la 
    documentation Scikit-Learn :
        `mean_squared_error`_
    
    .. _mean_squared_error: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_squared_error.html?highlight=mean_squared_error
    
    Parameters
    ----------
    estimator : PyTorchEstimators
        objet estimator de type regressor
    X : Iterable
        observations
    y_true : Iterable
        targets associées aux observations X
    kargs_fit : Dict[str, Any]
        dictionnaire des arguments nécéssaires au fit
    gap : int
        Permet de définir un gap entre l'apprentissage du modèle et la 
        prédiction. Par défaut 0, aucun gap. Dans la pratique le gap est à 
        minima égal à l'horizon de prédiction.
    idx_skip : Optional[Union[np.ndarray, List[int]]]
        indices des observation à exclure. Permet de limiter l'effet des black 
        swan pour cetain type de série.
    **kargs :
        paramètres associés à la fonction Scikit-Learn (voir la doc 
        Scikit-Learn).
    """
    check_estimator(
        estimator=estimator,
        estimator_type='regressor',
        fun_score='mean_squared_error_online'
    )
    y_pred = estimator.fit_online(
        X,
        predict = True,
        gap = gap,
        **kargs_fit
    )
    y_true, y_pred = skip_obs(y_true[gap:], y_pred, idx_skip, gap)
    return apply_metric_error(
        mean_squared_error,
        y_true,
        y_pred,
        **kargs
    )

def accuracy_score_online(estimator: PyTorchEstimators,
                          X: Iterable,
                          y_true: Iterable,
                          kargs_fit: Dict[str, Any],
                          gap: int=0,
                          idx_skip: Optional[Union[np.ndarray,
                                                   List[int]]]=None,
                          **kargs):
    r"""
    Fonction accuracy_score appliquée au contexte online. Voici la 
    documentation Scikit-Learn :
        `accuracy_score`_
    
    .. _accuracy_score: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html?highlight=accuracy_score
    
    Parameters
    ----------
    estimator : PyTorchEstimators
        objet estimator de type regressor
    X : Iterable
        observations
    y_true : Iterable
        targets associées aux observations X
    kargs_fit : Dict[str, Any]
        dictionnaire des arguments nécéssaires au fit
    gap : int
        Permet de définir un gap entre l'apprentissage du modèle et la 
        prédiction. Par défaut 0, aucun gap. Dans la pratique le gap est à 
        minima égal à l'horizon de prédiction.
    idx_skip : Optional[Union[np.ndarray, List[int]]]
        indices des observation à exclure. Permet de limiter l'effet des black 
        swan pour cetain type de série.
    **kargs :
        paramètres associés à la fonction Scikit-Learn (voir la doc 
        Scikit-Learn).
    """
    check_estimator(
        estimator=estimator,
        estimator_type='classifier',
        fun_score='accuracy_score_online'
    )
    y_pred = estimator.fit_online(
        X,
        predict=True,
        gap=gap,
        **kargs_fit
    )
    y_true, y_pred = skip_obs(y_true[gap:], y_pred, idx_skip, gap)
    return accuracy_score(y_true, y_pred, **kargs)

def roc_auc_score_online(estimator: PyTorchEstimators,
                         X: Iterable,
                         y_true: Iterable,
                         kargs_fit: Dict[str, Any],
                         keys: int=1,
                         gap: int=0,
                         idx_skip: Optional[Union[np.ndarray,
                                                  List[int]]]=None,
                         **kargs):
    r"""
    Fonction roc_auc_score appliquée au contexte online. Voici la 
    documentation Scikit-Learn :
        `roc_auc_score`_
    
    .. _roc_auc_score: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html?highlight=roc_auc_score

    Parameters
    ----------
    estimator : PyTorchEstimators
        objet estimator de type regressor
    X : Iterable
        observations
    y_true : Iterable
        targets associées aux observations X
    kargs_fit : Dict[str, Any]
        dictionnaire des arguments nécéssaires au fit
    keys : int
        colonne de sortie de prédiction correspondant à la classe testé
    gap : int
        Permet de définir un gap entre l'apprentissage du modèle et la 
        prédiction. Par défaut 0, aucun gap. Dans la pratique le gap est à 
        minima égal à l'horizon de prédiction.
    idx_skip : Optional[Union[np.ndarray, List[int]]]
        indices des observation à exclure. Permet de limiter l'effet des black 
        swan pour cetain type de série.
    **kargs :
        paramètres associés à la fonction Scikit-Learn (voir la doc 
        Scikit-Learn).
    """
    check_estimator(
        estimator=estimator,
        estimator_type='classifier',
        fun_score='roc_auc_score_online'
    )
    y_pred = estimator.fit_online(
        X,
        predict = True,
        needs_proba = True,
        gap = gap,
        **kargs_fit
    )
    if y_pred.shape[1] > 2:
        warnings.warn(
            "Attention, l'estimateur est multi-classes (pas bi-classes)."
        )
    y_true, y_pred = skip_obs(y_true[gap:], y_pred, idx_skip, gap)
    y_score = y_pred[:, keys]
    return roc_auc_score(y_true, y_score, **kargs)

def precision_score_online(estimator: PyTorchEstimators,
                           X: Iterable,
                           y_true: Iterable,
                           kargs_fit: Dict[str, Any],
                           gap: int=0,
                           idx_skip: Optional[Union[np.ndarray,
                                                    List[int]]]=None,
                           **kargs):
    r"""
    Fonction precision_score appliquée au contexte online. Voici la 
    documentation Scikit-Learn :
        `precision_score`_
    
    .. _precision_score: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html?highlight=precision_score
    
    Parameters
    ----------
    estimator : PyTorchEstimators
        objet estimator de type regressor
    X : Iterable
        observations
    y_true : Iterable
        targets associées aux observations X
    kargs_fit : Dict[str, Any]
        dictionnaire des arguments nécéssaires au fit
    gap : int
        Permet de définir un gap entre l'apprentissage du modèle et la 
        prédiction. Par défaut 0, aucun gap. Dans la pratique le gap est à 
        minima égal à l'horizon de prédiction.
    idx_skip : Optional[Union[np.ndarray, List[int]]]
        indices des observation à exclure. Permet de limiter l'effet des black 
        swan pour cetain type de série.
    **kargs :
        paramètres associés à la fonction Scikit-Learn (voir la doc 
        Scikit-Learn).
    """
    check_estimator(
        estimator=estimator,
        estimator_type='classifier',
        fun_score='precision_score_online'
    )
    y_pred = estimator.fit_online(
        X,
        predict = True,
        gap = gap,
        **kargs_fit
    )
    y_true, y_pred = skip_obs(y_true[gap:], y_pred, idx_skip, gap)
    return precision_score(y_true, y_pred, **kargs)

def precision_recall_fscore_support_online(estimator: PyTorchEstimators,
                                           X: Iterable,
                                           y_true: Iterable,
                                           kargs_fit: Dict[str, Any],
                                           gap: int=0,
                                           idx_skip: Optional[
                                               Union[np.ndarray,
                                                     List[int]]
                                               ]=None,
                                           **kargs):
    r"""
    Fonction precision_recall_fscore_support appliquée au contexte online. 
    Voici la documentation Scikit-Learn :
        `precision_recall_fscore_support`_
    
    .. _precision_recall_fscore_support: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html?highlight=precision_recall_fscore_support
    
    Parameters
    ----------
    estimator : PyTorchEstimators
        objet estimator de type regressor
    X : Iterable
        observations
    y_true : Iterable
        targets associées aux observations X
    kargs_fit : Dict[str, Any]
        dictionnaire des arguments nécéssaires au fit
    gap : int
        Permet de définir un gap entre l'apprentissage du modèle et la 
        prédiction. Par défaut 0, aucun gap. Dans la pratique le gap est à 
        minima égal à l'horizon de prédiction.
    idx_skip : Optional[Union[np.ndarray, List[int]]]
        indices des observation à exclure. Permet de limiter l'effet des black 
        swan pour cetain type de série.
    **kargs :
        paramètres associés à la fonction Scikit-Learn (voir la doc 
        Scikit-Learn).
    """
    check_estimator(
        estimator=estimator,
        estimator_type='classifier',
        fun_score='precision_recall_fscore_support_online'
    )
    y_pred = estimator.fit_online(
        X,
        predict = True,
        gap = gap,
        **kargs_fit
    )
    y_true, y_pred = skip_obs(y_true[gap:], y_pred, idx_skip, gap)
    return precision_recall_fscore_support(
        y_true, 
        y_pred,
        **kargs
    )

def check_estimator(estimator: PyTorchEstimators,
                    estimator_type: str,
                    fun_score: Optional[str]=None):
    r"""
    Fonction de test du type d'estimateur
    
    Parameters
    ----------
    estimator : PyTorchEstimators
        objet estimateur
    estimator_type : str
        type de l'estimateur souhaité
    fun_score : Optional[str]
        nom de la fonction testant l'estimateur. Par défaut None.
    """
    typ = ['regressor', 'classifier']
    if not estimator_type in typ:
        raise ValueError(
            f"Le type estimator_type: {estimator_type} doit être "
            f"{', '.join(typ)}."
        )
    if estimator._estimator_type != estimator_type:
        if fun_score is None:
            raise ValueError(
                f"L'estimateur entré n'est pas de type {estimator_type} mais "
                f"de type {estimator._estimator_type}. Il faut un "
                f"{estimator_type} pour utiliser cette métrique."
            )
        else:
            raise ValueError(
                f"L'estimateur entré de {fun_score} n'est pas de type "
                f"{estimator_type} mais de type {estimator._estimator_type}. "
                f"Il faut un {estimator_type} pour utiliser cette métrique."
            )

def reverse_score(loss_fun: Callable, *args, **kargs):
    r"""
    Décorateur d'inversement d'une fonction coût. Les fonctions en entrée de 
    l'argument scoring de la classe RandomizedSearchOnline sont considérées 
    comme étant des fonctions score par Scikit-Learn. Si la fonction de mesure 
    de performance est une fonction coût, il faut inverser les résultats afin 
    que le score le plus élevé corresponde au résultat de la fonction coût le 
    plus bas. Dans Scikit-Learn ce cas est traité en mutipliant le résultat 
    par -1 ce qui permet de préserver le sens physique de la fonction fonction 
    coût (il suffira de multiplier le résultat par -1). Cette stratégie est 
    préservée à l'aide de cette fonction.
    
    Parameters
    ----------
    loss_fun : Callable
        fonction coût à inverser
    *args :
        se référer à la fonction loss_fun utilisée ou custom
    **kargs :
        se référer à la fonction loss_fun utilisée ou custom
    """
    @wraps(loss_fun)
    def wrapper(*args, **kargs):
        res = loss_fun(*args, **kargs)
        return -1*res
    return wrapper

def apply_metric_error(fun: Callable,
                       y_true: Iterable,
                       y_pred: Iterable,
                       **kargs):
    r"""
    Application de la métrique fun. Si dans y_pred il y a un NaN ou un inf 
    alors retourne comme score Inf.
    
    Parameters
    ----------
    fun : Callable
        fonciton coût ou de score
    y_true : Iterable
        réalité terrain
    y_pred : Iterable
        prédiction
    **kargs:
        arguments de la fonction fun
    
    Returns
    -------
    score : float
        score issu de fun ou inf.
    """
    if all(~np.isnan(y_pred)) and all(~np.isinf(y_pred)):
        return fun(y_true, y_pred, **kargs)
    else:
        return np.inf

def skip_obs(y_true: Iterable,
             y_pred: Iterable,
             idx_skip: Optional[Iterable],
             gap: int):
    r"""
    Fonction permettant d'extraire certaines observations de l'évaluation.
    
    Parameters
    ----------
    y_true : Iterable
        array-like de la réalitée terrain
    y_pred : Iterable
        estimation de l'agorithme de ML
    idx_skip : Optional[Iterable]
        array-like indices des observation à exclure
    gap : int
        gap appliquer à l'évaluation
    """
    if idx_skip is None:
        idx_skip = []
    if not isinstance(idx_skip, np.ndarray):
        idx_skip = np.array(idx_skip)
    idx_skip = idx_skip[idx_skip > gap]-gap
    idx = np.arange(0, len(y_true))
    idx = idx[~np.isin(idx, idx_skip)]
    y_pred = y_pred[idx, :]
    if isinstance(y_true, list):
        y_true = [y_true[ii] for ii in idx]
    elif isinstance(y_true, np.ndarray):
        y_true = y_true[idx]
    elif isinstance(y_true, (DataFrame, Series,)):
        y_true = y_true.iloc[idx]
    else:
        raise AttributeError(
            "Le type de y_true n'est pas reconnu. Un array-like est soit "
            "de type list, ndarray, DataFrame ou Series, et non de type "
            f"{type(y_true)}."
        )
    return y_true, y_pred
