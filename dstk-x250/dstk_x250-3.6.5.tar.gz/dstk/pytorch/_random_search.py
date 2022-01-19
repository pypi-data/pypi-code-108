#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Méthodes utiles pour l'exploitation PyTorch

Created on Thu Oct 31 09:42:49 2019

@author: Cyrile Delestre
"""
from time import time
from collections import defaultdict
from functools import partial
from typing import (Union, Optional, Dict, List, Callable, NewType, Any,
                    Iterable, Tuple)

import numpy as np
from scipy.stats import rankdata

from pandas.core.frame import DataFrame

from sklearn import __version__ as sklearn_version
from sklearn.model_selection import ParameterSampler
from sklearn.model_selection._validation import _fit_and_score
from sklearn.base import clone
from joblib import Parallel, delayed

from dstk.utils import list_of_dict_2_dict_of_list as l2d
from ._base import BaseEnvironnement

PyTorchEstimators = NewType('PyTorchEstimators', BaseEnvironnement)

class RandomizedSearchOnline:
    r"""
    Classe de random search des hyper-paramètres dans un contexte d'algorithme 
    online. Le fonctionnement de RandomizedSearchOnline est très semblable au
    fonctionnement de RandomizedSearchCV de Scikit-Learn (pour plus de 
    détails sur les arguments, se référer à la doc Scikit-Learn 
    `RandomizedSearchCV`_).
    
    .. _RandomizedSearchCV: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.RandomizedSearchCV.html
    
    Parameters
    ----------
    estimator : PyTorchEstimators
        Un objet de type estimateur online. Les méthodes indispensables sont :
           - fit: (X, y=None)
               Fonction d'entrainement
           - fit_online: (X, y=None, predict=False)
               Fonction d'une phase online (entrainement + inférence)
    param_distributions : Dict[str, Any]
        Dictionnaire avec pour clefs les paramètres qu'on souhaite faire 
        varier (string). Pour chaque clef, une liste de l'univers possible 
        doit être décrite pour chaque paramètre.
    n_iter : int
        Nombre d'explorations distinctes dans l'univers des hyper-paramètres 
        de param_distributions (par défaut 10)
    scoring : Optional[Union[str, Callable, List[str], Tuple[str], Dict[str, Callable]]]
        None, string, list/tuple ou dict. Simple ou plusieurs fonction(s) de 
        scoring. Dans le cadre online, utiliser les fonctions de scoring 
        présentes dans utils.metrics. S'il s'agit d'une metrique custom, elle 
        doit avoir la forme :
            - my_metric_fun(estimator, X, y_true) 
                -> y_estim = estimator.fit_online(X, y_true, predict=True) 
                -> return metric_fun(y_estim, y_true)
        Par défaut, le classement se fait par ordre décroissant. Si fonction
        coût, prévoir une inversion du score dans la fonction de scoring.
    n_jobs : Optional[int]
        Nombre de jobs en parallèle. Si None, prendra 1 thread dans un 
        contexte joblib.parallel_backend. Si -1, prendra tous les threads du 
        processeur. Attention ! Si processeur multi-threadé, perte de 
        performances et prendre num_thread/2 (par défaut None).
    pre_dispatch : Optional[str, int]
        Contrôle le nombre de jobs devant être dispatchés durant l'éxécution. 
        Réduire le nombre permet d'éviter l'explosion de mémoire RAM (par 
        défaut '2*n_jobs').
    refit : Union[bool, str, Callable]
        Permet de réaliser le refit avec les paramètres ayant réalisé le 
        meilleur score. Pour de l'évaluation multi-metric, besoin d'un string 
        pour déterminer le choix du critère sur lequel sera fait le choix des 
        hyper-paramètres. refit peut également être une fonction qui retourne 
        ``best_index_`` pour un ``results_``. ``best_index_``, ``best_score_``,
        ``best_params_`` et ``best_estimator_`` seront des arguments existant 
        seulement s'il y a eu refit. (par défaut True)
    monte_carlo : int
        permet d'exécuter plusieur fois une topologie pour avec des scores 
        moyennés (par défaut 1, pas de Monte-Carlo).
    verbose : int
        Contrôle le niveau de verbosité (plus ce nombre est grand, plus des 
        informations seront marquées, par défaut 0).
    random_state : Optional[int]
        seed du ParameterSampler.
    error_score : str
        'raise' ou numeric. Comportement en cas d'erreur sur le score : 
        'raise' renvoit une erreur, sinon remplace par la valeur indiquée le 
        résultat du score (par exemple np.nan, par défaut 'raise').
    return_train_score : bool
        retourne le ou les scores sur le dataset de train (en plus de l'éval). 
        Cependant, le classement des scores se fera toujours sur le dataset 
        d'éval.
    
    Notes
    -----
    Si l'estimateur entré dans l'arguement estimator ne possède pas les 
    méthodes fit et fit_online, retourne une erreur.
    """
    def __init__(self,
        estimator: PyTorchEstimators,
        param_distributions: Dict[str, Any],
        n_iter: int=10,
        scoring: Optional[Union[str, Callable, List[str], Tuple[str], Dict[str, Callable]]]=None,
        n_jobs: Optional[int]=None,
        refit: Union[bool, str, Callable]=True,
        monte_carlo: int=1,
        verbose: int=0,
        pre_dispatch: Optional[Union[str, int]]='2*n_jobs',
        random_state: Optional[int]=None,
        error_score: str='raise',
        return_train_score: bool=False
    ):
        self.estimator = estimator
        self.param_distributions = param_distributions
        self.n_iter = n_iter
        self.scoring = scoring
        self.n_jobs = n_jobs
        self.refit = refit
        self.monte_carlo = monte_carlo
        self.verbose = verbose
        self.pre_dispatch = pre_dispatch
        self.random_state = random_state
        self.error_score = error_score
        self.return_train_score = return_train_score
        
        if not hasattr(estimator, 'fit'):
            raise TypeError("La fonction fit n'est pas implémentée à "
                            "l'estimator.")
        if not hasattr(estimator, 'fit_online'):
            raise TypeError(
                f"La classe {self.__name__} est destinée à des modèles Online "
                "qui possèdent comme méthode fit_online. Cette dernière n'est "
                "pas implémentée, vérifier qu'il s'agit bien d'une approche "
                "Online et voir si l'héritage BaseRegessorOnline ou "
                "BaseClassifierOnline a bien été hérité."
            )
        if not isinstance(monte_carlo, int) and monte_carlo < 1:
            raise TypeError(
                "La variable monte_carlo doit être un entier int supérieur "
                "ou égale à 1."
            )

    def fit(
        self,
        X: Iterable,
        y: Optional[Iterable]=None,
        idx_stop_train: Optional[int]=None,
        gap: int=0,
        idx_skip: Optional[Union[np.ndarray, List[int]]]=None,
        **fit_params
    ):
        r"""
        Applique le fit de l'estimateur sur l'univers des hyper-paramètres.
        
        Parameters
        ----------
        X : Iterable
            array-like ou Dataset de PyTorch. Dataset d'entrainement. Les 
            observations doivent rester dans l'ordre de dépendance.
        y : Iterable
            array-like [n-samples] ou [n-samples, n-output], optionnel. Target 
            relative à X. Si None, apprentissage non supervisé.
        idx_stop_train : Optional[int]
            Indice de l'horizon d'apprentissage.
        gap : int
            Permet de définir un gap entre l'apprentissage du modèle et la 
            prédiction. Par défaut 0, aucun gap. Dans la pratique le gap est 
            à minima égal à l'horizon de prédiction.
        idx_skip : Optional[Union[np.ndarray, List[int]]]
            array-like d'indexe que l'on souhaite extraire de l'évaluation 
            (par exemple les zones d'événements rares, etc.). Important : Si 
            on  dans le cadre d'un random search il faut soustraire 
            idx_stop_train aux indices à skiper.
        **fit_params :
            Paramètres passés à la fonction fit de l'estimateur.
        """
        if idx_stop_train is None or isinstance(idx_stop_train, (float, str)):
            raise ValueError(
                "La variable idx_stop_train est de type "
                f"{type(idx_stop_train).__name__}. Ce doit être un integer "
                "(int) représentant un indice."
            )
        if isinstance(X, (np.ndarray, DataFrame)):
            len_dataset = X.shape[0]
        else:
            len_dataset = len(X)
        if idx_stop_train >= len_dataset-1:
            raise ValueError(
                "L'indice idx_stop_train doit être strictement inférieur à "
                "la taille du dataset X."
            )

        fit_params_scorers = fit_params.copy()
        fit_params_scorers['build'] = False
        if callable(self.scoring):
            self.multimetric_ = False
            scorers = {
                'score': partial(
                    self.scoring,
                    gap = gap,
                    idx_skip = idx_skip,
                    kargs_fit = fit_params_scorers
                )
            }
        elif isinstance(self.scoring, dict):
            self.multimetric_ = True
            scorers = {
                kk: partial(
                    ss,
                    gap = gap,
                    idx_skip = idx_skip,
                    kargs_fit = fit_params_scorers
                ) for kk, ss in self.scoring.items()
            }
        elif isinstance(self.scoring, (list, tuple)):
            self.multimetric_ = True
            scorers = {
                ii: partial(
                    ii,
                    gap = gap,
                    idx_skip = idx_skip,
                    kargs_fit = fit_params_scorers
                ) for ii in self.scoring
            }
        else:
            raise ValueError(
                "Le paramètre scoring doit prendre soit une fonction de "
                "scoring soit un dictionnaire contenant des fonctions score "
                "ou une liste ou tuple de fonctions score. Pas "
                f"{self.scoring}."
            )

        if self.multimetric_:
            if self.refit is not False and (
                    not isinstance(self.refit, str) or
                    self.refit not in scorers) and not callable(self.refit):
                raise ValueError(
                    "Si multi-métric, il faut que le refit soit True, dans "
                    "ce cas la meilleur métrique sera utilisée. Ou sinon un "
                    "callable ou le nom correspondant à l'une des mesures de "
                    "performance contenues dans scoring. Et non "
                    f"refit={self.refit}."
                )
            else:
                refit_metric = self.refit
        else:
            refit_metric = 'score'

        train, test = (
            list(range(idx_stop_train)),
            list(range(idx_stop_train, len_dataset))
        )
        candidate_params = list(
            ParameterSampler(
                param_distributions = self.param_distributions,
                n_iter = self.n_iter,
                random_state = self.random_state
            )
        )
        n_candidates = len(candidate_params)

        print(
            f"Fitting {n_candidates} candidates with {self.monte_carlo} "
            f"Monte-Carlo iterations. {n_candidates*self.monte_carlo} "
            "models should be fitted.",
            flush=True
        )

        estimator = clone(self.estimator)
        all_candidate_params = []
        all_out = []
        with Parallel(n_jobs = self.n_jobs,
                      verbose = self.verbose,
                      pre_dispatch = self.pre_dispatch) as parallel:
            # La fonction _fit_and_score retourne dans l'ordre :
            # [train_scores, test_scores, fit_time, score_time]
            out = parallel(
                delayed(_fit_and_score)(
                    estimator = clone(estimator),
                    X = X,
                    y = y,
                    train = train,
                    test = test,
                    scorer = scorers,
                    verbose = self.verbose,
                    parameters = parameters,
                    fit_params = fit_params,
                    return_train_score = self.return_train_score,
                    return_n_test_samples = True,
                    return_parameters = False,
                    return_times = True,
                    return_estimator = False,
                    error_score = self.error_score
                )
                for parameters in candidate_params 
                for mc in range(self.monte_carlo)
            )
        if len(out) == 0:
            raise ValueError(
                "La fonction fit ne s'est pas bien déroulée. Le problème "
                "doit venir de param_distributions. Est-il non-vide ?"
            )
        if len(out) != n_candidates*self.monte_carlo:
            raise ValueError(
                "Le nombre de résultats en sortie de la validation différe "
                "du nombre de tests souhaité. Il y a eu {} exécution(s) alors "
                "que {} étai(en)t attendue(s)."
                .format(len(out), n_candidates*self.monte_carlo)
            )
        all_candidate_params.extend(candidate_params)
        all_out.extend(out)

        results = self._format_results(all_candidate_params, scorers, all_out)

        if self.refit or not self.multimetric_:
            if callable(self.refit):
                self.best_index_ = self.refit(results)
                if not isinstance(self.best_index_, (int, np.integer)):
                    raise TypeError(
                        "best_index_ n'est pas un integer."
                    )
                if (self.best_index_ < 0 or 
                        self.best_index_ >= len(results["params"])):
                    raise IndexError(
                        "``best_index_`` est out of range, doit être compris "
                        "entre 0 et {} et vaut {}."
                        .format(len(results["params"]), self.best_index_)
                    )
            else:
                self.best_index_ = (
                    results[f"rank_test_{refit_metric}"].argmin()
                )
                self.best_score_ = (
                    results[(
                        f"mean_test_{refit_metric}" if self.monte_carlo > 1
                        else f"test_{refit_metric}"
                    )][self.best_index_]
                )
            self.best_params_ = results["params"][self.best_index_]

        if self.refit:
            self.best_estimator_ = clone(estimator)\
                .set_params(**self.best_params_)
            refit_start_time = time()
            if y is not None:
                self.best_estimator_.fit(X, y, **fit_params)
            else:
                self.best_estimator_.fit(X, **fit_params)
            refit_end_time = time()
            self.refit_time_ = refit_end_time - refit_start_time

        self.scorer_ = scorers if self.multimetric_ else scorers['score']

        self.results_ = results

        return self

    def _format_results(
        self,
        candidate_params: List[Dict[str, Any]],
        scorers: Union[Callable, Dict[str, Callable]],
        out: List[float]
    ):
        r"""\
        Fontion de formatage des résultats interne à la classe.
        
        Parameters
        ----------
        candidate_params : List[Dict[str, Any]]
            liste des dictionnaires générée par ParameterSampler.
        scorers : Union[Callable, Dict[str, Callable]]
            dictionnaire ou callable des scores.
        out : List[float]
            sortie des apprentissages avec en sortie :
                - return_train_score = True
                    [train_scores, test_scores, fit_time, score_time]
                - return_train_score = False
                    [test_scores, fit_time, score_time]
        
        Returns
        -------
        results : Dict[str, Any]
            dictionnaire contenant les paramètres avec le rang associé en 
            fonction des scores.
        
        Notes
        -----
        Cette méthode est inspiré de la méthode _format_results qu'on 
        peut trouver dans Scikit-Learn à quelques adaptations près.
        """
        n_candidates = len(candidate_params)
        if sklearn_version < '0.20':
            if self.return_train_score:
                (train_score_dicts, test_score_dicts,
                 test_sample_counts, fit_time, score_time) = zip(*out)
            else:
                (test_score_dicts, test_sample_counts, fit_time,
                 score_time) = zip(*out)
        else:
            out_ = l2d(out)
            fit_failed = out_['fit_failed']
            test_score_dicts = out_['test_scores']
            # test_sample_counts = out_['n_test_samples']
            fit_time = out_['fit_time']
            score_time = out_['score_time']
            if self.return_train_score:
                train_score_dicts = out_['train_scores']

        test_scores = {
            key: np.asarray(
                [score[key] for score in test_score_dicts]
            ) for key in test_score_dicts[0]
        }
        if self.return_train_score:
            train_scores = {
                key: np.asarray(
                    [score[key] for score in train_score_dicts]
                ) for key in train_score_dicts[0]
            }

        results = {}

        def _store(key_name, array, monte_carlo=False, rank=False):
            """Fonction interne d'aide au remplissage de results_"""
            if self.monte_carlo > 1:
                array = (
                    np.array(array, dtype=np.float64)
                    .reshape(n_candidates, self.monte_carlo)
                )
                if monte_carlo:
                    for mc_i in range(self.monte_carlo):
                        results[f"mc{mc_i}_{key_name}"] = array[:, mc_i]
                if key_name != 'fit_failed':
                    array_means = np.average(array, axis=1)
                    results[f"mean_{key_name}"] = array_means
                    array_stds = np.std(array, axis=1)
                    results[f"std_{key_name}"] = array_stds
                else:
                    array_means = np.average(array, axis=1)
                    results[f"ratio_{key_name}"] = array_means
                if rank:
                    results[f"rank_{key_name}"] = np.asarray(
                        rankdata(-array_means, method='min'),
                        dtype=np.int32
                    )
            elif self.monte_carlo == 1:
                array = np.array(array, dtype=np.float64).ravel()
                results[f"{key_name}"] = array
                if rank:
                    results[f"rank_{key_name}"] = np.asarray(
                        rankdata(-array, method='min'),
                        dtype=np.int32
                    )
            else:
                raise AttributeError(
                    "L'attribue monte_carlo doit être un entier supérieur "
                    f"ou égal à 1 et non égal à {self.monte_carlo}."
                )

        if sklearn_version >= '0.20':
            _store('fit_failed', fit_failed)
        _store('fit_time', fit_time)
        _store('score_time', score_time)

        # Utilise un MaskedArray pour masquez tous les endroits où les 
        # paramètres ne sont pas applicable pour ce candidat.
        # Utilise defaultdict car chaque candidat peut ne pas contenir tous 
        # les paramètres.
        param_results = defaultdict(
            partial(
                np.ma.MaskedArray,
                np.empty(n_candidates,),
                mask=True,
                dtype=object
            )
        )
        for cand_i, params in enumerate(candidate_params):
            for name, value in params.items():
                # Un masque entièrement vide est créé pour la première 
                # occurence de `name` `f"param_{name}"`.
                # La définition de la valeur à un index démasque également 
                # cet index.
                param_results[f"param_{name}"][cand_i] = value
        
        results.update(param_results)
        # Store la liste des paramètre
        results['params'] = candidate_params

        for scorer_name in scorers.keys():
            _store(
                key_name = f"test_{scorer_name}",
                array = test_scores[scorer_name],
                monte_carlo = True,
                rank = True
            )
            if self.return_train_score:
                _store(
                    key_name = f"train_{scorer_name}",
                    array = train_scores[scorer_name],
                    monte_carlo = True
                )

        return results

    def _check_refit(self):
        r"""
        Méthodes privées de check refit.
        """
        if not hasattr(self, 'best_estimator_'):
            raise ValueError(
                "Le modèle best_estimator_ n'existe pas. Il ce peut que "
                "vous n'ayez pas utilisé l'option refit de "
                "RandomizedSearchOnline ou vous n'avez pas encore exécuté "
                "le fit."
            )

    def predict(self, X: Iterable):
        r"""
        Méthode permettant de wrapper le predict de l'estimateur.
        
        Parameters
        ----------
        X : Iterable
            observations
        """
        self._check_refit()
        return self.best_estimator_.predict(X)

    def predict_proba(self, X: Iterable):
        r"""
        Méthode permettant de wrapper le predict_broba de l'estimateur pour 
        un classifier.
        
        Parameters
        ----------
        X : Iterable
            observations
        """
        self._check_refit()
        if self.estimator._estimator_type != 'classifier':
            raise ValueError(
                "L'estimateur n'est pas un classifier, il s'agit d'un {}. "
                "Il n'a donc pas de méthode predict_proba."
                .format(self.estimator._estimator_type)
            )
        return self.best_estimator_.predict_proba(X)

    def fit_online(self, **kargs):
        r"""
        Méthode permettant de wrapper le fit_online.
        
        Parameters
        ----------
        kargs :
            arguments de fit_online de l'estimateur.
        """
        self._check_refit()
        return self.best_estimator_.fit_online(**kargs)
