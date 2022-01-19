#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe pour wrapper facilement un modèle de machine learning personnel avec 
Scikit-Learn.

Created on Mon Nov 23 13:31:25 2020

@author: Cyrile Delestre
"""

from collections.abc import Iterable
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from joblib import Parallel, delayed
from tqdm import tqdm

class Base(BaseEstimator):
    r"""
    Classe générique de BaseEstimator Scikit-Learn qui implémente une
    exécution compatible avec les Pipeline où les éléments doivent être
    traités un à un si ils sont dans une liste ou un itérable. Elle est
    compatible pour les Classifier et les Regressor. Elle nécessite
    l'implémentation de udf_fit(X, y, **kargs) et
    udf_predict(self, X, **kargs).
    
    Parameters
    ----------
    n_jobs : int
        nombre de processeurs en parallèle
    verbose : bool
        Si True bare de progression de process.
    
    Notes
    -----
    Cette classe n'est pas à utiliser directement (sauf si nécessaire). Il
    est préférable de se reporter sur la classe Regressor s'il s'agit d'un
    regresseur ou Classifier s'il s'agit d'un classifieur.
    
    See also
    --------
    Regressor, Classifier
    """
    def __init__(self, n_jobs: int, verbose: bool):
        self.n_jobs = n_jobs
        self.verbose = n_jobs

    def _fit_iter(self, X: Iterable, y: Iterable, **kargs):
        r"""
        Itération de l'apprentissage.
        """
        fit = delayed(self.udf_fit)
        if y is None:
            iterator = tqdm(
                X, 
                desc = f"{self.__class__.__name__}",
                mininterval = 0.5
            ) if self.verbose else X

            with Parallel(n_jobs=self.n_jobs) as par:
                par(fit(x, **kargs) for x in iterator)
        elif isinstance(y, Iterable):
            iterator = tqdm(
                zip(X, y),
                desc = f"{self.__class__.__name__}",
                mininterval = 0.5
            ) if self.verbose else zip(X, y)

            with Parallel(n_jobs=self.n_jobs) as par:
                par(fit(*x, **kargs) for x in iterator)
        else:
            raise AttributeError(
                "y doit être soit None et dans ce cas X doit contenir la "
                f"target, soit être un Iterable, ici y est de type {type(y)}."
            )

    def udf_fit(self, X: Iterable, y: Iterable, **kargs):
        r"""
        Fit unitaire.
        """
        raise NotImplementedError(
            "Il faut implémenter la méthode udf_fit(self, X, y, **kargs) à "
            f"la classe {self.udf_fit.__name__} qui hérite de la classe "
            "Transformer."
        )

    def fit(self, X: Iterable, y: Optional[Iterable]=None, **kargs):
        r"""
        Fonction fit pour être ISO avec Scikit-Learn
        
        Parameters
        ----------
        X : Iterable
            pour un traitement itératif un Iterable
        y : Optional[Iterable]
            target de l'entrainement.
        **kargs :
            arguments propres au transformer
        """
        if isinstance(X, (pd.DataFrame, np.ndarray,)):
            self.udf_fit(X, y, **kargs)
        elif isinstance(X, Iterable):
            self._fit_iter(X, y, **kargs)
        else:
            raise AttributeError(
                "L'argument X de fit doit être un Iterable."
            )
        return self

    def _predict_iter(self, X: Iterable, **kargs):
        r"""
        Itération de la prédiction.
        """
        iterator = tqdm(
            X,
            desc = f"{self.__class__.__name__}",
            mininterval = 0.5
        ) if self.verbose else X

        pred = delayed(self.udf_predict)
        with Parallel(n_jobs=self.n_jobs) as par:
            return par(pred(x, **kargs) for x in iterator)

    def udf_predict(self, X: Iterable, **kargs):
        r"""
        Prédiction unitaire.
        """
        raise NotImplementedError(
            "Il faut implémenter la méthode udf_predict(self, X, **kargs) à "
            f"la classe {self.udf_predict.__name__} qui hérite de la classe "
            "Transformer."
        )

    def predict(self, X: Iterable, **kargs):
        r"""
        Fonction predict pour être ISO avec Scikit-Learn
        
        Parameters
        ----------
        X : Iterable
            pour un traitement itératif un Iterable
        **kargs :
            arguments propres au transformer
        """
        if isinstance(X, (pd.DataFrame, np.ndarray,)):
            return self.udf_predict(X, **kargs)
        elif isinstance(X, Iterable):
            return self._predict_iter(X, **kargs)
        else:
            raise AttributeError(
                "L'argument X de predict doit être un Iterable."
            )

class Regressor(Base, RegressorMixin):
    r"""
    Classe générique Regressor héritant de la classe Base.
    
    Classe générique de BaseEstimator Scikit-Learn qui implémente une
    exécution compatible avec les Pipeline où les éléments doivent être
    traités un à un si ils sont dans une liste ou un itérable. Elle nécessite
    l'implémentation de udf_fit(X, y, **kargs) et
    udf_predict(self, X, **kargs).
    
    Parameters
    ----------
    n_jobs : int
        nombre de processeurs en parallèle
    verbose : bool
        Si True bare de progression de process.
    
    Notes
    -----
    A utiliser si l'algorithme de régression n'est pas standard à
    Scikit-Learn. Par exemple Gensim, Tensorflow, PyTorch, etc.
    
    A noter que pour PyTorch il est conseillé d'utiliser dstk.pytorch 
    wrapper d'un modèle PyTorch à Scikit-Learn.
    
    Examples
    --------
    Considérons que je possède un modèle SuperAlgoRegressor qui n'est pas
    prototypé Scikit-Learn.
    
    >>> from dataclasses import dataclass
    >>> from sklearn.preprocessing import RobustScaler
    >>> from sklearn.pipeline import Pipeline
    >>> ...
    >>> from mon_projet import SuperAlgoRegressor
    >>> from dstk.ml import Regressor
    >>> 
    >>> @dataclass
    >>> class SuperAlgo2Sklear(Regressor):
    >>>     "Classe SuperAlgoRegressor vers Scikit-Learn."
    >>>     model: SuperAlgoRegressor
    >>>     n_jobs: int=1
    >>>     verbose: bool=False
    >>> 
    >>>     def udf_fit(self, X, y, lr=1e-3):
    >>>         self.model.train(X, y, lr)
    >>> 
    >>>     def udf_predict(self, X, weights = None):
    >>>         return self.model.estimation(X, weights)
    
    >>> scal = RobustScaler()
    >>> mon_model = SuperAlgoRegressor(**kargs_de_mon_SuperAlgoRegressor)
    >>> reg = SuperAlgo2Sklear(mon_model, verbose=True)
    >>> pipe = Pipeline([('scale', scal), ('regressor', reg)])
    >>> pipe.fit(X, y, lr=1e-5)
    
    See also
    --------
    Classifier, dstk.pytorch
    """
    def __init__(self, n_jobs: int, verbose: bool):
        self.n_jobs = n_jobs
        self.verbose = verbose

class Classifier(Base, ClassifierMixin):
    r"""
    Classe générique Classifier héritant de la classe Base.
    
    Classe générique de BaseEstimator Scikit-Learn qui implémente une
    exécution compatible avec les Pipeline où les éléments doivent être
    traités un à un si ils sont dans une liste ou un itérable. Elle nécessite
    l'implémentation de udf_fit(X, y, **kargs) et udf_predict(X, **kargs)
    et udf_predict_proba(X, **kargs).
    
    Parameters
    ----------
    n_jobs : int
        nombre de processeurs en parallèle
    verbose : bool
        Si True bare de progression de process.
    
    Notes
    -----
    A utiliser si l'algorithme de classification n'est pas standard à
    Scikit-Learn. Par exemple Gensim, Tensorflow, PyTorch, etc.
    
    A noter que pour PyTorch il est conseillé d'utiliser dstk.pytorch wrapper 
    d'un modèle PyTorch à Scikit-Learn.
    
    Examples
    --------
    Considérons que je possède un modèle SuperAlgoClassifier qui n'est pas
    prototypé Scikit-Learn.
    
    >>> from dataclasses import dataclass
    >>> from sklearn.preprocessing import RobustScaler
    >>> from sklearn.pipeline import Pipeline
    >>> ...
    >>> from mon_projet import SuperAlgoClassifier
    >>> from dstk.ml import Classifier
    >>> 
    >>> @dataclass
    >>> class SuperAlgo2Sklear(Classifier):
    >>>     "Classe SuperAlgoClassifier vers Scikit-Learn."
    >>>     model: SuperAlgoClassifier
    >>>     n_jobs: int=1
    >>>     verbose: bool=False
    >>> 
    >>>     def udf_fit(self, X, y, lr=1e-3):
    >>>         self.model.train(X, y, lr)
    >>> 
    >>>     def udf_predict(self, X, weights = None):
    >>>         return self.model.estimation(X, weights)
    >>> 
    >>>     def udf_predict_proba(self, X, weights = None)
    >>>         return self.model.estimation(X, weights, proba=True)
    
    >>> scal = RobustScaler()
    >>> mon_model = SuperAlgoClassifier(**kargs_de_mon_SuperAlgoClassifier)
    >>> clf = SuperAlgo2Sklear(mon_model, verbose=True)
    >>> pipe = Pipeline([('scale', scal), ('classifier', clf)])
    >>> pipe.fit(X, y, lr=1e-5)
    
    See also
    --------
    Regressor, dstk.pytorch
    """
    def __init__(self, n_jobs: int, verbose: bool):
        self.n_jobs = n_jobs
        self.verbose = verbose

    def _predict_proba_iter(self, X, **kargs):
        r"""
        Itération de la prédiction.
        """
        iterator = tqdm(
            X,
            desc = f"{self.__class__.__name__}",
            mininterval = 0.5
        ) if self.verbose else X

        pred = delayed(self.udf_predict_proba)
        with Parallel(n_jobs=self.n_jobs) as par:
            return par(pred(x, **kargs) for x in iterator)

    def udf_predict_proba(self, X: Iterable, **kargs):
        r"""
        Prédiction unitaire.
        """
        raise NotImplementedError(
            "Il faut implémenter la méthode udf_predict_proba(self, X, **kargs) "
            f"à la classe {self.udf_predict_proba.__name__} qui hérite de la "
            "classe Transformer."
        )

    def predict_proba(self, X: Iterable, **kargs):
        r"""\
        Fonction predict_proba pour être ISO avec Scikit-Learn

        Parameters
        ----------
        X : Iterable
            DataFrame, pour un traitement itératif un Iterable
        **kargs :
            arguments propres au transformer
        """
        if isinstance(X, (pd.DataFrame, np.ndarray,)):
            return self.udf_predict_proba(X, **kargs)
        elif isinstance(X, Iterable):
            return self._predict_proba_iter(X, **kargs)
        else:
            raise AttributeError(
                "L'argument X de predict_proba doit être un Iterable."
            )
