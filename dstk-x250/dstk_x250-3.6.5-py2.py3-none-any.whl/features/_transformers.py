#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe et fonction facilitant le wrapping Scikit-Learn d'un transformer 
personalisé.

Created on Mon Nov 23 12:12:30 2020

@author: Cyrile Delestre
"""

from collections.abc import Iterable, Callable

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from joblib import Parallel, delayed
from tqdm import tqdm

def make_transformer(udf_transform: Callable,
                     n_jobs: int=1,
                     verbose: bool=False):
    r"""
    Instentiatieur de classe Transformer, sert à éviter d'écrire une classe 
    directement.
    
    Parameters
    ----------
    udf_transform : Callable
        fonction de transformation défini par l'utilisateur (user difined 
        function) qui doit avoir pour prototypage :
            udf_transform(X, **kargs)
    n_jobs : int
        nombre de processeurs en parallèle
    verbose : int
        Si True bare de progression de process.
    
    Notes
    -----
    Si le transformer que l'on souhaite créer nécessite la surcharge de la 
    fonction fit alors il est obliger de passer par la définition d'une 
    classe.
    
    De même udf_transform doit être une fonction simple, sinon il est très 
    conseiller de passer par la définition d'une classe.
    
    Examples
    --------
    >>> from dataclasses import dataclass
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> from sklearn.pipeline import Pipeline
    >>> from dstk.features import make_transformer
    >>> from dstk.utils import check_dataframe
    >>> 
    >>> def udf_transform(X, order_col=['col_3', 'col_1', 'col_2', 'col_0']):
    >>>     # check_dataframe vérifie s'il s'agit bien d'une DataFrame 
    >>>     # et que les colonnes de order_col sont bien présentes
    >>>     check_dataframe(X, order_col)
    >>>     return X[order_col]
    >>> 
    >>> orderer = make_transformer(udf_transform)
    >>> clf = RandomForestClassifier()
    >>> pipe = Pipeline([('order_col', orderer), ('rf', clf)])
    >>> pipe.fit(X, y)
    
    See also
    --------
    Transformer
    """
    if not isinstance(udf_transform, Callable):
        raise AttributeError(
            "udf_transform doit être une fonction Callable et non de type "
            f"{type(udf_transform)}."
        )
    trans = Transformer(n_jobs=n_jobs, verbose=verbose)
    trans.udf_transform = udf_transform
    return trans

class Transformer(BaseEstimator, TransformerMixin):
    r"""
    Classe générique de transformation Scikit-Learn qui implémente une 
    exécution compatible avec les Pipeline où les éléments doivent être 
    traités un à un si ils sont dans une liste ou un itérable. 
    
    Parameters
    ----------
    n_jobs : int
        nombre de processeurs en parallèle
    verbose : bool
        Si True bare de progression de process.
    
    Notes
    -----
    Il est important d'implémenter la méthode udf_transform(self, X, **kargs)  
    et surcharger les autres  méthodes si besoin.
    
    Examples
    --------
    Exemple très simple d'un transformer utilisant la classe Transfomer qui 
    permet d'ordonner les colonnes d'une DataFramme en fonction d'un ordre 
    souhaité.
    
    >>> from dataclasses import dataclass
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> from sklearn.pipeline import Pipeline
    >>> from dstk.features import Transformer
    >>> from dstk.utils import check_dataframe
    >>> 
    >>> @dataclass
    >>> class SortColumns(Transformer):
    >>>     "Classe qui ordonne les colonnes d'une DataFrame."
    >>>     order_col: list
    >>>     n_jobs: int=1
    >>>     verbose: bool=False
    >>>
    >>>     def udf_transform(self, X):
    >>>         # check_dataframe vérifie s'il s'agit bien d'une DataFrame 
    >>>         # et que les colonnes de self.order_col sont bien présentes
    >>>         check_dataframe(X, self.order_col)
    >>>         return X[self.order_col]
    
    >>> orderer = SortColumns(['col_3', 'col_1', 'col_2', 'col_0'], n_jobs=2)
    >>> clf = RandomForestClassifier()
    >>> pipe = Pipeline([('order_col', orderer), ('rf', clf)])
    >>> pipe.fit(X, y)
    
    See also
    --------
    make_transformer
    """
    def __init__(self, n_jobs: int, verbose: bool):
        self.n_jobs = n_jobs
        self.verbose = n_jobs

    def fit(self, X: Iterable, y: None=None):
        r"""
        Fonction fit pour être ISO avec Scikit-Learn
        
        Parameters
        ----------
        X : Iterable
            Observations
        y : None
            pour être ISO avec Scikit-Learn
        """
        return self

    def _transform_iter(self, X: Iterable, **kargs):
        r"""
        Itération de transformations.
        
        Parameters
        ----------
        X : Iterable
            Observations
        """
        iterator = tqdm(
            X, 
            desc = f"{self.__class__.__name__}",
            mininterval = 0.5
        ) if self.verbose else X

        trans = delayed(self.udf_transform)
        with Parallel(n_jobs=self.n_jobs) as par:
            return par(trans(x, **kargs) for x in iterator)

    def udf_transform(self, X: Iterable, **kargs):
        r"""\
        Transformation unitaire.
        
        Parameters
        ----------
        X : Iterable
            Observations
        """
        raise NotImplementedError(
            "Il faut implémenter la méthode udf_transform(self, X, **kargs) "
            f"à la classe {self.__name__} qui hérite de la classe "
            "Transformer."
        )

    def transform(self, X: Iterable, **kargs):
        r"""\
        Méthode générique scikit-learn pour la transformation.

        Parameters
        ----------
        X : Iterable
            Array-like, pour un traitement itératif un Iterable quelconque
        :**kargs: arguments propres au transformer
        """
        if isinstance(X, (pd.DataFrame, np.ndarray,)):
            return self.udf_transform(X, **kargs)
        elif isinstance(X, Iterable):
            return self._transform_iter(X, **kargs)
        else:
            raise AttributeError(
                "L'argument X de transform doit être un Iterable."
            )
