#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe de wrapping Scikit-Learn pour PyTorch. Base regressor.

Created on Mon Oct 21 14:42:57 2019

@author: Cyrile Delestre
"""
from typing import Union, Dict, List, Tuple, Any, Optional, Iterable

import numpy as np
from pandas.core.frame import DataFrame
from sklearn.base import RegressorMixin
from torch import no_grad
from torch.utils.data import Dataset

from ._base import BaseEnvironnement
from . import check_tensor_dict, check_tensor

class BaseRegressor(BaseEnvironnement, RegressorMixin):
    r"""
    Classe d'implémentation des Regressor pour être compatible Scikit-Learn. 
    Elle hérite de BaseEnvironnement et RegressorMixin.

    Notes
    -----
    La méthode constituant BaseRegressor :
        predict:
            méthode de prédiction compatible avec le prototypage Scikit-Learn 
            predict(X, rnn_hidden_state, **kargs).
    """
    _estimator_type = 'regressor'
    def predict(
        self,
        X: Union[Dataset,
                 np.ndarray,
                 DataFrame,
                 List[Dict[str, Any]],
                 Tuple[Dict[str, Any]],
                 Dict[str, Any]],
        nan_inf: bool=True,
        fill_nan: float=0,
        add_dim_batch: bool=False,
        **kargs
    ):
        r"""
        Méthode de prédiction compatible Scikit-Learn.
        
        Parameters
        ----------
        X : Union[Dataset, np.ndarray, DataFrame, List[Dict[str, Any]], Tuple[Dict[str, Any]], Dict[str, Any]]
            Features du modèle, pour le bon fonctionnement via Scikit-Learn et
            de son utilisation classique, X peut être de différents types
                - Dataset: Classe Dataset de PyTorch, doit sortir un 
                    dictionnaire contenant tous les arguments indispensables au
                    calcul du modèle de la fonction forward.
                - list: liste de dictionnaire contenant tous les arguments
                    indispensables au calcul du modèle de la fonction forward.
            Attention : La première dimension doit être consacrée à celle du
            batch. Si qu'une seule observation alors la première dimension sera
            de dimension 1.
        nan_inf : bool
            traitre les NaN si l'algorithme à divergé et met les valeurs inf 
            à la plus grande valeur possible du type du numpy array.
        fill_nan : float
            valeur de remplacement des NaN.
        add_dim_batch : bool (=False)
            ajoute la dimension du batch si elle n'est pas présente.

        Returns
        -------
        res : np.ndarray
            retourne le résultat au format numpy array de la fonction de 
            classification forward
        """
        self.eval()
        with no_grad():
            if isinstance(X, (Dataset, list, tuple,)):
                res = []
                for data in X:
                    data = check_tensor_dict(data, add_dim_batch=add_dim_batch)
                    res.append(self.forward(**data).detach().numpy())
                res = np.concatenate(res, axis=0)
                return np.nan_to_num(res, nan=fill_nan) if nan_inf else res
            elif isinstance(X, np.ndarray):
                res = self.forward(check_tensor(X), **kargs).detach().numpy()
                return np.nan_to_num(res, nan=fill_nan) if nan_inf else res
            elif isinstance(X, dict):
                X = check_tensor_dict(X, add_dim_batch=add_dim_batch)
                res = self.forward(**X).detach().numpy()
                return np.nan_to_num(res, nan=fill_nan) if nan_inf else res
            else:
                raise AttributeError(
                    f"Le type de X {type(X)} n'est pas prise en compte."
                )

class BaseRegressorOnline(BaseRegressor):
    r"""
    Classe d'implémentation des Regressor dans un contexte online pour être 
    compatible à Scikit-Learn. Elle hérite de BaseRegressor.
    
    Notes
    -----
    Les méthodes constituant BaseRegressorOnline :
        save_weights :
            surchage de la méthode save_weights de BaseEnvironnement afin de 
            coller au contexte online.
        fit :
            surcharge de la méthode fit de BaseEnvironnement afin de coller au 
            context online.
        fit_online :
            implémentation de l'apprentissage online avec possibilité de 
            réaliser une prédiction à la volée.
    """
    def save_model(self, path: Optional[str]=None, **kargs_dump):
        r"""
        Méthode permettant de sauvegarder simplement les paramètres et les
        poids du modèle (sans la structure de réseau) ainsi que l'état de 
        l'optimizer pour une utilisation online. Utilise Pickle.
        
        Parameters
        ----------
        path : Optional[str]
            path directory du modèle, si None retourne les données binaires de 
            Pickle.dumps()
        **kargs_dump : 
            paramètres attachés à Pickle.dump(obj, file, **kargs_dump) si 
            path est un chemin ou a Pickles.dump(obj, **kargs_dump) si None.
        """
        return super().save_model(
            path=path,
            save_optimizer_state=True,
            **kargs_dump
        )

    def fit(self, X, y=None, **kargs):
        r"""
        Méthode de fit (wrapper vers Scikit-learn). Pour l'apprentissage la
        partie preprocessing doit être faite au préalable. La fonction est
        conçue pour fonctionner avec du multiprocessing. Donc un identifiant
        unique est donné à chaque session d'entrainement via uuid avec pour
        protocole 1.
        
        Parameters
        ----------
        X : Iterable
            Dataset PyTorch contenant dans un dictionnaire les infos 
            nécessaires pour l'apprentissage du modèle.
                - Attention :
                    à la sortie du DataLoader (donc via collate_fn ou 
                    directement via DataSet de PyTorch), il faut que le 
                    dictionnaire possède les noms présents dans le forward de 
                    la sous-classe du modèle.
        y : Optional[Iterable]
            Pour être ISO avec Scikit-learn. L'ensemble de l'apprentissage 
            passera via X et le système DataSet et DataLoader de PyTorch.
        **kargs :
            le reste des arguments de la méthode fit de la classe 
            BaseEnvironnement.
        """
        super().fit(
            X=X,
            y=y,
            eval_dataset=None,
            nb_epoch=1,
            kargs_dataloader=dict(
                batch_size=1,
                shuffle=False,
                drop_last=False
            ),
            callbacks=[],
            **kargs
        )
        return self

    def fit_online(
        self,
        X: Iterable,
        y: Optional[Iterable]=None,
        predict: bool=False,
        needs_proba: bool=False,
        gap: int=0,
        treat_nan_inf: bool=True,
        fill_nan: float=0,
        **fit_kargs
    ):
        r"""
        Méthode d'apprentissage online avec possibilité d'inférence à la volée.
        
        Parameters
        ----------
        X : Iterable
            Dataset PyTorch contenant dans un dictionnaire les infos
            nécessaires pour l'apprentissage du modèle.
                - Attention :
                    à la sortie du DataLoader (donc via collate_fn 
                    ou directement via DataSet de PyTorch), il faut que le 
                    dictionnaire possède les noms présents dans le forward de 
                    la sous-classe du modèle.
        y : Optional[Iterable]
            Pour être ISO avec Scikit-learn. L'ensemble de l'apprentissage 
            passera via X et le système DataSet et DataLoader de PyTorch.
        predict : bool
            permet de faire la phase d'inférence à la volée. Par défaut False.
        gap : int
            Permet de définir un gap entre l'apprentissage du modèle et la 
            prédiction. Par défaut 0, aucun gap. Dans la pratique le gap 
            est à minima égal à l'horizon de prédiction
        treat_nan_inf : bool
            traitre les NaN de la prédiction si l'algorithme à divergé et met 
            les valeurs inf à la plus grande valeur possible du type du numpy 
            array.
        fill_nan : float
            valeur de remplacement des NaN pour la prédiction.
        **fit_kargs :
            le reste des arguments de la méthode fit de la classe 
            BaseEnvironnement.
        """
        if 'build' in fit_kargs.keys():
            fit_kargs_ = dict(fit_kargs)
            if fit_kargs_['build']:
                fit_kargs_['build'] = False
                self.build()
        else:
            fit_kargs_ = dict(fit_kargs)
            fit_kargs_['build'] = False
        if predict:
            res = []
        for ii, data in enumerate(X):
            self.fit(data, y=y, **fit_kargs_)
            if predict:
                if gap > 0:
                    if ii+gap < len(X):
                        data_eval = X[ii+gap]
                        res.append(
                            self.predict(
                                data_eval,
                                treat_nan_inf=treat_nan_inf,
                                fill_nan=fill_nan,
                                add_dim_batch=True
                            )
                        )
                else:
                    res.append(
                        self.predict(
                            data,
                            treat_nan_inf=treat_nan_inf,
                            fill_nan=fill_nan,
                            add_dim_batch=True
                        )
                    )
        if predict:
            return np.concatenate(res, axis=0)
        return self
