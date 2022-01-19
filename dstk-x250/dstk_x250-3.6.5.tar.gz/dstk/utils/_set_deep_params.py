#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonction set_params_deep
^^^^^^^^^^^^^^^^^^^^^^^^

Created on Mon Nov 23 13:23:47 2020

@author: Cyrile Delestre
"""

from warnings import warn

from sklearn.base import BaseEstimator

def set_params_deep(model: BaseEstimator, warnning: bool=True, **params):
    r"""
    Permet de changer l'ensemble de paramètres à partir d'un certain niveau 
    de l'attribution des noms de variables dans le standard Scikit-Learn 
    "nv_1__niv_2__niv_3__param".
    
    Parameters
    ----------
    model : BaseEstimator
        model Scikit-Learn (Pipeline, algo ML, grid search, etc.).
    warnning : bool
        affiche un warning si le paramètre recherché n'est pas présent dans 
        le modèle
    **params :
        paramètres à modifier au format key__params. Si on souhaite changer 
        tous les paramètres qui possède le même nom alors juste mettre params.
    
    Examples
    --------
    >>> from sklearn.pipeline import Pipeline
    >>> ...
    >>> from dstk.utils import set_params_deep
    
    >>> ...
    >>> 
    >>> pipe = Pipeline(...)
    >>> 
    >>> # Par exemple si on souhaite changer tous les n_jobs, max_depth et
    >>> # verbose dans l'ensemble de la Pipeline pipe
    >>> set_params_deep(
    >>>     pipe,
    >>>     n_jobs=1,
    >>>     verbose=False,
    >>>     niv_1__niv_2__max_depth=42
    >>> )
    """
    if not (hasattr(model, 'get_params') and hasattr(model, 'set_params')):
        raise AttributeError(
            "La modèle doit être un objet de type Scikit-Learn et doit être "
            "doté d'une méthode get_params et set_params. L'objet model est "
            f"ici de type {type(model)}."
        )
    list_params = model.get_params().keys()
    new_params = dict()
    for kk in params:
        keys = kk.split('__')
        if len(keys) == 1:
            filt = list(
                filter(
                    lambda x: x.split('__')[-1] == kk,
                    list_params
                )
            )
        else:
            filt = list(
                filter(
                    lambda x: (
                        len(x.split('__')) >= len(keys)
                        and
                        all(
                            [
                                ii == tt
                                for ii, tt in zip(x.split('__'), keys[:-1])
                            ]
                        )
                        and x.split('__')[-1] == keys[-1]
                    ),
                    list_params
                )
            )
        if warnning and len(filt) == 0:
            if len(keys) == 1:
                warn(
                    f"Le paramètre {kk} n'est pas présent dans le modèle."
                )
            else:
                warn(
                    f"La clef {'__'.join(keys[:-1])} avec le paramètre "
                    f"{keys[-1]} n'est pas présent dans le modèle."
                )
        if len(filt) > 0:
            new_params.update({param: params[kk] for param in filt})
    if len(new_params) > 0:
        model.set_params(**new_params)
