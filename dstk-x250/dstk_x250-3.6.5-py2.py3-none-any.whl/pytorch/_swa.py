#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Stochastic Weight Averaging (SWA)

Created on Tue Jan 19 06:46:56 2021

@author: Cyrile Delestre
"""

import os
from copy import deepcopy
from dataclasses import dataclass
from typing import List, Dict, Union, Optional, NewType, Any, Callable
from collections import OrderedDict
from itertools import chain
from warnings import warn

import numpy as np
from torch import Tensor, no_grad
from sklearn.model_selection import ShuffleSplit, StratifiedShuffleSplit
from torch.utils.data import Dataset, DataLoader, Subset
from torch.optim.swa_utils import AveragedModel, SWALR, update_bn

from dstk.pytorch import (CallbackInterface, CallbackHandler,
                          ProgressBarCallback, FitState, FitControl,
                          check_tensor)
from dstk.utils.meta_interface import SuperclassDocstring
from dstk.utils.errors import DivergenceError

BATCH_NORM_LAYERS = [
    'BatchNorm1d',
    'BatchNorm2d',
    'BatchNorm3d',
    'GroupNorm',
    'SyncBatchNorm',
    'InstanceNorm1d',
    'InstanceNorm2d',
    'InstanceNorm3d',
    'LayerNorm'
]

# Permet d'éviter une initialisation circulaire via l'import de
# BaseEnvironnement
PyTorchEstimators = NewType('PyTorchEstimators', Any)

@dataclass
class SaveStateSWACallback(CallbackInterface, metaclass=SuperclassDocstring):
    r"""
    Classe de gestion des poids de la méthode SWA permettant de préserver le 
    meilleur modèle durant le processus SWA.

    Parameters
    ----------
    old_res_loss : float
        Valeur loss atteinte pendant la phase d'apprentissage classique.
    path_save : Optional[str] (=None)
        Chemin (absolu ou relatif) où le modèle par early stopping sera 
        préservé. Si None, les paramètres seront sauvegardés en RAM. 
        Cependant il est déconseillé de le faire car les réseaux profonds 
        peuvent être très gourmands en espace RAM. De même, en cas de 
        plantage, un état du réseau pouvant être satisfaisant est préservé 
        sur le disque dur.
    early_stopping_rounds : Optional[int] (=None)
        Nombre d'itérations (epoch) sans amélioration. Si None pas de 
        early stopping, le modèle sauvegardé sera donc le meilleur modèle 
        durant l'ensemble des époques.
    minimize : bool (=True)
        Indique si l'objectif est de minimiser la fonciton coût (True) ou 
        de la maximiser (False).
    normalise : bool (=False)
        Indique si une couche de normalisation est présente dans le modèle. 
        Dans ce cas l'évaluation durant l'apprentissage n'est pas possible.
    verbose : bool (=False)
        Indique les informations de gain de performance.

    Notes
    -----
    Cette classe n'a pas pour but d'être utilisée directement, mais est 
    instanciée dans la classe 
    :mod:`~dstk.pytorch._swa.StochasticWeightAveraging`.
    """
    old_res_loss: float
    path_save: Optional[str] = None
    early_stopping_rounds: Optional[int] = None
    minimize: bool = True
    normalise: bool = False
    verbose: bool = False

    def __post_init__(self):
        self.iter_stop: int = 0
        self.best_epoch: int = 0
        self.best_iter: int = 0

    def _extract_swa_state(
        self,
        model: PyTorchEstimators,
        swa_model: AveragedModel
    ):
        r"""
        Méthode privée qui permet d'extraire les poids du modèle SWA et les 
        renommer pour correspondre aux noms des poids du modèle.

        Parameters
        ----------
        model : PyTorchEstimators
            instance du modèle PyTorch.
        swa_model : AveragedModel
            instance du modèle SWA.
        """
        swa_weights = model._extract_state(swa_model)
        swa_weights = OrderedDict(
            ('.'.join(kk.split('.')[1:]), vv)
            for kk, vv in swa_weights.items() if kk.startswith('module')
        )
        return swa_weights

    def end_eval(
        self,
        model: PyTorchEstimators,
        data: List[Dict[str, Tensor]],
        state: FitState,
        control: FitControl,
        res_loss: float,
        swa_model: AveragedModel) -> None:
        if (
                res_loss < self.old_res_loss 
                if self.minimize else 
                res_loss > self.old_res_loss
        ):
            if self.verbose:
                print(
                    "\n[SWA] Gain de performance époque/itération : "
                    f"{state.n_epoch_swa+1}/{state.n_iter_swa+1} ;\n"
                    f"Gain de performance {state.loss_name} :\n"
                    f"{self.old_res_loss} -> {res_loss}.\n",
                    flush=True
                )
            self.iter_stop = 0
            self.old_res_loss = res_loss
            self.best_epoch = state.n_epoch_swa
            self.best_iter = state.n_iter_swa
            swa_model.update_parameters(model)
            if self.path_save is None:
                self.state_dict = self._extract_swa_state(model, swa_model)
            else:
                model.save_weights(
                    f"{self.path_save}/{state.id_process}.model",
                    state_dict=self._extract_swa_state(model, swa_model)
                )
        elif (
                self.early_stopping_rounds is not None and 
                (
                    res_loss >= self.old_res_loss 
                    if self.minimize else
                    res_loss <= self.old_res_loss
                )
        ):
            self.iter_stop += 1
            if self.iter_stop >= self.early_stopping_rounds:
                control.training_stop = True

    def end_train(
        self,
        model: PyTorchEstimators,
        data: List[Dict[str, Tensor]],
        state: FitState,
        control: FitControl,
        res_loss: float,
        swa_model: AveragedModel,
        eval_dataset: Optional[DataLoader]
    ) -> None:
        if self.verbose:
            print(
                f"\n[SWA] Meilleure époque/iteration : {self.best_epoch+1}/"
                f"{self.best_iter+1}\n"
                f"Meilleure performance {state.loss_name} : "
                f"{self.old_res_loss}.\n",
                flush=True
            )
        if self.best_iter > 0:
            if self.normalise:
                update_bn(loader=data, swa_model=swa_model);
                if eval_dataset is not None:
                    if self.path_save is None:
                        self.state_dict = self._extract_swa_state(swa_model)
                    else:
                        model.save_weights(
                            f'{self.path_save}/{state.id_processes}.model',
                            state_dict=self._extract_swa_state(swa_model)
                        )
            if self.path_save is None:
                model.load_state_dict(self.state_dict)
            else:
                model.load_weights(
                    f"{self.path_save}/{state.id_process}.model"
                )
                os.remove(f"{self.path_save}/{state.id_process}.model")


@dataclass
class LRSchedulerSWACallback(CallbackInterface, metaclass=SuperclassDocstring):
    r"""
    Classe de gestion du learning rate pour la méthode Stochastic Weight 
    Averaging (SWA).

    Parameters
    ----------
    anneal_epochs : int
        Nombre d'époque pour la phase de recuisson.
    swa_lr : float
        Valeur du learning rate minimal.
    annealing_strategy : str (='cos')
        Stratégie de recuissson :
            - "cos" : stratégie cosinus (par défaut) ;
            - "linear" : stratégie linéaire.
    last_epoch : int (=-1)
        Indice de la dernière époque.

    Notes
    -----
    Cette classe n'a pas pour but d'être utilisée directement, mais est 
    instanciée dans la classe 
    :mod:`~dstk.pytorch._swa.StochasticWeightAveraging`.
    """
    anneal_epochs: int
    swa_lr: float
    anneal_strategy: str = 'cos'
    last_epoch: int = -1

    def begin_train(self,
                    model: PyTorchEstimators,
                    data: List[Dict[str, Tensor]],
                    state: FitState,
                    control: FitControl,
                    res_loss: float,
                    swa_model: AveragedModel) -> None:
        self.scheduler = SWALR(
            optimizer=model.optimizer,
            anneal_epochs=self.anneal_epochs,
            swa_lr=self.swa_lr,
            anneal_strategy=self.anneal_strategy,
            last_epoch=self.last_epoch
        )

    def end_epoch(self,
                  model: PyTorchEstimators,
                  data: List[Dict[str, Tensor]],
                  state: FitState,
                  control: FitControl,
                  res_loss: float,
                  swa_model: AveragedModel) -> None:
        self.scheduler.step()

@dataclass
class StochasticWeightAveraging:
    r"""
    CLasse du processus `Stochastic Weight Averaging (SWA)`_ qui permet de 
    robustifier l'estimateur en moyennant les poids du modèle.

    .. _Stochastic Weight Averaging (SWA): https://arxiv.org/abs/1803.05407

    Parameters
    ----------
    nb_epoch : int
        Nombre d'époques réservé au WSA. Si 0 pas de processus SWA.
    lr : float
        Niveau le plus bas de descente pour le lr scheduler du processus SWA.
    nb_anneal : int (=2)
        Nombre de période fait par le lr scheduler du processus SWA.
    strategy : str (='cos')
        Stratégie du lr scheduler du processus SWA, soit 'cos', ou 'linear'.
    inner_ratio : float (=0.7)
        Ratio d'observation conjoint dans la base d'apprentissage du modèle et 
        du processus SWA. Pour avoir les deux même bases mettre à 1 et pour 
        avoir 2 bases d'apprentissage complétement différentes mettre à 0. 
        Apporter de nouvelles observations pendant le processus SWA permet 
        d'augmenter son efficacité.
    stratified : bool (=False)
        Permet de stratifier les observations communes dans les bases 
        d'apprentissage du train et du processus SWA. Utilisable seulement 
        si le modèle est un classifieur.
    random_state : int (=42)
        random state pour déterminer le mélange des observations pour la 
        construction des deux bases d'apprentissage train et SWA.
    early_stopping_rounds : Optional[int] (=None)
        Nombre d'itérations (epoch) sans amélioration. Si None pas de 
        early stopping, le modèle sauvegardé sera donc le meilleur modèle 
        durant l'ensemble des époques.
    path_save : Optional[str] (=None)
        Chemin (absolu ou relatif) où le modèle par early stopping sera 
        préservé. Si None, les paramètres seront sauvegardés en RAM. 
        Cependant il est déconseillé de le faire car les réseaux profonds 
        peuvent être très gourmands en espace RAM. De même, en cas de 
        plantage, un état du réseau pouvant être satisfaisant est préservé 
        sur le disque dur.
    minimize: bool (=True)
        Indique si une couche de normalisation est présente dans le modèle. 
        Dans ce cas l'évaluation durant l'apprentissage n'est pas possible.
    verbose : bool (=True)
        Indique les informations de gain de performance.

    Notes
    -----
    Le comportement de la classe est de préserver les poids moyennés si le 
    modèle SWA possède de meilleures performances que l'évaluation du modèle 
    de l'évaluation précédente.

    **Aucune de ces méthodes ne doivent être appelées par l'utilisateur**. 
    Elles sont utilisées automatiquement durant le processus d'apprentissage 
    de la méthode :func:`~dstk.pytorch._base.BaseEnvironnement.fit`.

    Warning
    -------
    Si le modèle possède une couche de normalisation alors l'évaluation du 
    modèle au cours de l'apprentissage n'est plus possible. Il sera alors 
    pris à chaque époque l'impact du modèle actuel et une normalisation 
    est appliquée à la fin du processus SWA.
    """
    nb_epoch: int
    lr: float
    nb_anneal: int = 2
    strategy: str = "cos"
    inner_ratio: float = 0.7
    stratified: bool = False
    random_state: int = 42
    early_stopping_rounds: Optional[int] = None
    path_save: Optional[str] = None
    minimize: bool = True
    verbose: bool = True

    def copy(self):
        r"""
        Créer une copie de l'objet.
        """
        return deepcopy(self)

    def init(self,
             model: PyTorchEstimators,
             res_loss: float):
        r"""
        
        """
        self.normalise = any(
            chain.from_iterable(
                map(
                    lambda y: map(
                        lambda x: f'{x}' in f'{y[1]}',
                        BATCH_NORM_LAYERS
                    ),
                    model.named_children()
                )
            )
        )
        if self.normalise:
            warn(
                "Une couche de Batch Normalization a été détectée. Il "
                "ne sera pas possible d'évaluer les performances du "
                "processus SWA durant les époques. Donc toutes les "
                "itérations seront prises en compte dans le modèle "
                "final."
            )
        callbacks = [
            SaveStateSWACallback(
                old_res_loss=res_loss,
                path_save=self.path_save,
                normalise=self.normalise,
                minimize=self.minimize,
                early_stopping_rounds=self.early_stopping_rounds,
                verbose=self.verbose
            ),
            LRSchedulerSWACallback(
                anneal_epochs=self.nb_epoch,
                swa_lr=self.lr,
                anneal_strategy=self.strategy,
                last_epoch=-1
            )
        ]
        if self.verbose:
            callbacks.append(ProgressBarCallback(_swa_process=True))
        self.callbacks = CallbackHandler(callbacks)
        self._estimator_type = model._estimator_type

    def _divergence(self, loss: float):
        r"""
        Méthode interne d'alerte de divergence du modèle pendant sa phase 
        d'apprentissage.
        """
        if np.isnan(loss) or np.isinf(loss):
            raise DivergenceError(
                """Verger ! L'algorithme a dit "verger" !"""
            )

    def _eval_step(self,
                   swa_model: AveragedModel,
                   data: List[Dict[str, Any]],
                   field_target: str,
                   loss_fn: Callable,
                   kargs_loss: Dict[str, Any]):
        r"""
        Méthode privée d'une étape d'évaluation.

        Parameters
        ----------
        swa_model : AveragedModel
            Modèle PyTorch d'AveragedModel.
        data : List[Dict[str, Any]]
            Liste de dictionnaires sur les données d'un mini-batch.
        field_target : str
            Nom du champs de la target.
        loss_fn : Callable
            Fonction coût PyTorch.
        kargs_loss : Dict[str, Any]
            Dictionnaire d'arguments à utiliser dans la fonction de coût 
            loss_fun.

        Returns
        -------
        loss : float
            Valeur de la fonction coût au travers du mini-batch.
        """
        swa_model.eval()
        with no_grad():
            output = swa_model.forward(**data)
            target = check_tensor(data[field_target])
            loss = loss_fn(output, target, **kargs_loss)
        loss = loss.detach()
        self._divergence(loss)
        return loss

    def _iter_eval(self,
                   model: PyTorchEstimators,
                   swa_model: AveragedModel,
                   eval_dataset: DataLoader,
                   field_target: str,
                   loss_fn: Callable,
                   kargs_loss: Optional[Dict[str, Any]],
                   state: FitState,
                   control: FitControl,
                   list_callbacks: List[CallbackInterface]):
        r"""
        Méthode interne exécutant la phase d'évaluation durant l'apprentissage 
        du processus SWA.Cette étape peut être appelée à la fin d'une époque 
        ou durant l'exécution de l'époque (dépend de l'argument iter_eval de 
        la méthode :func:`~dstk.pytorch._base.BaseEnvironnement.fit`).

        Parameters
        ----------
        model : PyTorchEstimators
            Modèle d'origine.
        swa_model : AveragedModel
            Modèle PyTorch d'AveragedModel.
        eval_dataset : DataLoader
            Dataset d'évaluation au format DataLoeader généré dans la méthode 
            :func:`~dstk.pytorch._base.BaseEnvironnement.fit`.
        field_target : str
            Nom du champs target.
        loss_fn : Callable
            Fonction coût à minimiser (utiliser les fonctions présentes dans 
            torch.nn.functional). Si la fonction est une fonction custom, elle 
            doit avoir le prototypage suivant :
                - loss_fn(y_estim, y_true, reduction='sum', **kargs)
            avec une implémentation de réduction 'sum' pour les phases 
            d'évaluation et 'mean' pour les phases d'apprentissage.
        kargs_loss : Optional[Dict[str, Any]]
            Dictionnaire d'arguments à utiliser dans la fonction de coût 
            loss_fun.
        state : FitState
            Etat de l'apprentissage (instancié dans la méthode 
            :func:`~dstk.pytorch._base.BaseEnvironnement.fit`).
        control : FitControl
            Contrôle de l'apprentissage (instancié dans la méthode 
            :func:`~dstk.pytorch._base.BaseEnvironnement.fit`).
        list_callbacks : List[CallbackInterface]
            Liste des callback permettant de contôler l'apprentissage durant 
            la phase d'évaluation.
        """
        swa_model_int = deepcopy(swa_model)
        swa_model_int.update_parameters(model)
        list_callbacks.begin_eval(
            model=model,
            data=eval_dataset,
            state=state,
            control=control,
            res_loss=None,
            swa_model=swa_model
        )
        loss_eval = 0
        for jj, eval_batch in enumerate(eval_dataset):
            list_callbacks.begin_eval_step(
                model=model,
                data=eval_batch,
                state=state,
                control=control,
                res_loss=loss_eval/(jj+1),
                swa_model=swa_model
            )
            try:
                loss_eval += self._eval_step(
                    swa_model=swa_model_int,
                    data=eval_batch,
                    field_target=field_target,
                    loss_fn=loss_fn,
                    kargs_loss=kargs_loss
                )
            except DivergenceError as error:
                control.diverge = True
                warn(error.msg)
                break
        list_callbacks.end_eval(
            model=model,
            data=eval_dataset,
            state=state,
            control=control,
            res_loss=loss_eval/(jj+1),
            swa_model=swa_model
        )

    def fit(self,
            model: PyTorchEstimators,
            eval_dataset: Optional[DataLoader],
            loss_fn: Callable,
            kargs_loss: Optional[Dict[str, Any]],
            field_target: str,
            iter_eval: Optional[int],
            collate_fn: Callable,
            batch_size: int,
            shuffle: bool,
            drop_last: bool,
            num_workers: int,
            state: FitState,
            control: FitControl):
        r"""
        Processus d'apprentissage SWA.
        
        Parameters
        ----------
        model : PyTorchEstimators
            Modèle d'origine.
        eval_dataset : Optional[DataLoader]]
            DataLoader PyTorch contenant les observations et les targets 
            d'évaluation. Si eval_set est None alors pas de early stopping 
            et évaluation des performances sur les données d'entrainement 
            (déconseillé car très fort risque d'overfitting).
        loss_fn : Optional[Callable] (=None)
            Fonction coût à minimiser (utiliser les fonctions présentes dans 
            torch.nn.functional). Si la fonction est une fonction custom, elle 
            doit avoir le prototypage suivant :
                - loss_fn(y_estim, y_true, reduction='sum', **kargs)
            avec une implémentation de réduction 'sum' pour les phases 
            d'évaluation et 'mean' pour les phases d'apprentissage.
        kargs_loss : Dict[str, Any] (=dict())
            Dictionnaire d'arguments à utiliser dans la fonction de coût 
            loss_fun. Si il n'y a pas d'arguments, mettre un dictionnaire 
            vide.
        field_target : str
            Nom du champ contenu dans X de la target. Par défaut "target". 
            Attention l'implémentation de la fonction collate_fn peut faire 
            changer le nom de la target.
        iter_eval : Optional[int]
            Nombre d'itération entre deux évaluations. Actif seulement si 
            eval_set est non None. Si iter_eval est à None (défini par 
            défaut) les évaluations du modèle seront à la fin des époques. 
            Si un entier positif est renseigné les évaluations auront lieu 
            tous les iter_eval itérations d'apprentissage.
        collate_fn : Optional[Callable]
            Fonction de sortie de DataLoader permettant la concaténation en 
            batch des différentes observations du mini-batch.
        batch_size : int
            taille du mini-batch. Pris en compte seulement si dataloader = 
            True.
        shuffle : bool 
            Permet de mélanger à chaque époque les observations. Pris en 
            compte seulement si dataloader = True.
        drop_last : bool
            Drop les dernières observations si le rapport entre le nombre 
            d'observations et la taille du mini-batch est non entier. Pris en 
            compte seulement si dataloader = True.
        num_workers : int
            Nombre de process du DataLoader. Par défaut 0 correspondant à du 
            mono-thread. Pris en compte seulement si dataloader = True.
                - Attention :
                    1 -> mono-threadé mais isolé de l'environnement 
                    (Picklelisé). Si le DataLoader est utilisé dans un 
                    environnement Sciki-Learn multi-processing (par exemple 
                    pour un RandomizedSearchCV) il est très important de 
                    mettre cet argument à 0 pour que la DataLoader tourne 
                    dans l'environnement principal de Python. Dans le cas 
                    contraire le processus plantera.
        state : FitState
            Etat de l'apprentissage (instancié dans la méthode 
            :func:`~dstk.pytorch._base.BaseEnvironnement.fit`).
        control : FitControl
            Contrôle de l'apprentissage (instancié dans la méthode 
            :func:`~dstk.pytorch._base.BaseEnvironnement.fit`).
        """
        if self.verbose:
            print(
                "Début de la procédure de Stochastic Weight Averagin (SWA) "
                "avec :\n"
                f"    - {self.nb_epoch} époques ;\n"
                f'    - {self.nb_anneal} nombres de "recuissons" ;\n'
                f"    - {self.strategy} stratégies ;\n"
                f"    - un ratio d'intersection de {self.inner_ratio}."
            )
        swa_model = AveragedModel(model)
        swa_model.update_parameters(model)

        if not isinstance(self.X_swa, DataLoader):
            dataset = DataLoader(
                self.X_swa,
                collate_fn=collate_fn,
                shuffle=shuffle,
                drop_last=drop_last,
                batch_size=batch_size,
                num_workers=num_workers
            )
        else:
            dataset = self.X_swa

        state.nb_epoch_swa = self.nb_epoch
        self.callbacks.begin_train(
            model=model,
            data=dataset,
            state=state,
            control=control,
            res_loss=None,
            swa_model=swa_model
        )
        for n_epoch in range(self.nb_epoch):
            state.n_epoch_swa = n_epoch
            loss_epoch = 0
            self.callbacks.begin_epoch(
                model=model,
                data=dataset,
                state=state,
                control=control,
                res_loss=loss_epoch,
                swa_model=swa_model
            )
            for ii, batch in enumerate(dataset):
                state.n_iter_swa = ii
                if (
                    eval_dataset and
                    model._mod(n_epoch*state.epoch_max_steps+ii, iter_eval) == 0
                ):
                    self._iter_eval(
                        model=model,
                        swa_model=swa_model,
                        eval_dataset=eval_dataset,
                        field_target=field_target,
                        loss_fn=loss_fn,
                        kargs_loss=kargs_loss,
                        state=state,
                        control=control,
                        list_callbacks=self.callbacks
                    )
                    if control.diverge or control.training_stop:
                        break
                self.callbacks.begin_step(
                    model=model,
                    data=batch,
                    state=state,
                    control=control,
                    res_loss=None,
                    swa_model=swa_model
                )
                try:
                    loss_step = model._train_step(
                        data=batch,
                        field_target=field_target,
                        loss_fn=loss_fn,
                        kargs_loss=kargs_loss
                    )
                    loss_epoch += loss_step
                    self.callbacks.end_step(
                        model=model,
                        data=batch,
                        state=state,
                        control=control,
                        res_loss=loss_step,
                        swa_model=swa_model
                    )
                except DivergenceError as error:
                    control.diverge = True
                    warn(error.msg)
                    break
            loss_epoch /= (ii+1)
            self.callbacks.end_epoch(
                model=model,
                data=dataset,
                state=state,
                control=control,
                res_loss=loss_epoch,
                swa_model=swa_model
            )
            if eval_dataset and iter_eval is None:
                self._iter_eval(
                    model=model,
                    swa_model=swa_model,
                    eval_dataset=eval_dataset,
                    field_target=field_target,
                    loss_fn=loss_fn,
                    kargs_loss=kargs_loss,
                    state=state,
                    control=control,
                    list_callbacks=self.callbacks
                )
            if control.diverge or control.training_stop:
                break
        self.callbacks.end_train(
            model=model,
            data=dataset,
            state=state,
            control=control,
            res_loss=None,
            swa_model=swa_model,
            eval_dataset=eval_dataset
        )

def cut_dataset(
    model: PyTorchEstimators,
    data: Union[Dataset, DataLoader, List[Dict[str, Any]]],
    *,
    ratio: float=0.5,
    stratified: bool=False,
    target_field: str='target',
    random_state: int=42
):
    r"""
    Fonction qui découpe un dataset en deux datasets en fonction d'un taux de 
    recouvrement des observations.

    Parameters
    ----------
    model: PyTorchEstimators
        Modèle d'apprentissage PyTorch.
    data : Union[Dataset, DataLoader, List[Dict[str, Any]]]
        Dataset ou list de dictionnaire des observations.
    ratio : float (=0.5)
        Taux de recouvrement des observations entre les deux datasets.
    stratified : bool (=False)
        Permet de stratifier la répartition en fonction des classes de la 
        target (ne fonctionne que si il s'agit d'un classifieur).
    target_field : str (='target')
        Précise le champs target si il y a une stratification (sinon non 
        utilisé).
    random_state : int (=42)
        Random state de la répartition des observations.

    Returns
    -------
    DatasetTrain : Union[Datast, Dataset, List[Dict[str, Tensor]]]
        Dataset utilisé pour la phase d'entrainement
    """
    if ratio < 0 or ratio > 1:
        raise AttributeError(
            "swa_inner_ratio doit être compris entre 0 et 1 "
            f"(inclus). Ici il vaut {ratio} !"
        )
    if stratified and model._estimator_type != 'classifier':
        raise AttributeError(
            "Pour l'approche stratifiée de l'intersection jointe il faut "
            "que le modèle soit un classifier, or il s'agit d'une "
            f"{model._estimator_type} !"
        )
    if isinstance(data, DataLoader):
        is_dataloader = True
        dl_args = {
            kk: vv for kk, vv in data.__dict__.items()
            if not kk.startswith('_')
            and not kk in ('dataset', 'batch_sampler')
        }
        data = data.dataset
    else:
        is_dataloader = False
    size = len(data)
    idx_ = np.arange(size)
    y = None
    if ratio < 1 and ratio > 0:
        if stratified:
            split = StratifiedShuffleSplit(
                n_splits=1,
                train_size=int(ratio*size),
                random_state=random_state
            )
            y = list(map(lambda x: x[target_field], data))
        else:
            split = ShuffleSplit(
                n_splits=1,
                train_size=int(ratio*size),
                random_state=random_state
            )
        idx_over, idx_rest = next(split.split(idx_, y))
    elif ratio == 1:
        idx_over, idx_rest = idx_, np.array([])
    elif ratio == 0:
        idx_over, idx_rest = np.array([]), idx_
    idx_train = np.r_[
        idx_rest[:int(idx_rest.shape[0]//2)],
        idx_over
    ]
    idx_swa = np.r_[
        idx_rest[int(idx_rest.shape[0]//2):],
        idx_over
    ]
    if is_dataloader:
        return (
            DataLoader(dataset=Subset(data, idx_train), **dl_args),
            DataLoader(dataset=Subset(data, idx_swa), **dl_args)
        )
    elif isinstance(data, Dataset):
        return Subset(data, idx_train), Subset(data, idx_swa)
    else:
        return (
            [data[ii] for ii in idx_train],
            [data[ii] for ii in idx_swa]
        )
