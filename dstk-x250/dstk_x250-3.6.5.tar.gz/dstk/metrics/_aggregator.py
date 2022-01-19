#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe aggrégatrice des mesures.

Created on Sun Nov 22 12:41:19 2020

@author: Cyrile Delestre
"""

from sys import version_info

import numpy as np
import pandas as pd

if version_info.major >= 3 and version_info.minor >= 8:
    class Aggregator:
        r"""
        Classe agrégatrice pour le décorateur 
        :func:`~dstk.metrics._metrics.sniffer` offrant un comportement par 
        défaut. Il est possible de faire hériter cette classe pour construire 
        d'autres agrégateurs ou changer son comportement.
        
        Elle doit contenir la méthode make_message qui renvoit un 
        dictionnaire. Rien n'y oblige, mais en standard elle renvoit tourjours 
        au moins le type de la variable avec le mot clef 'type'.
        
        Examples
        --------
        Voici un exemple de surchage de la classe Aggregator où l'on souhaite 
        changer le comportement sur les listes et ajouter un nouveau type 
        MonObj.
        
        >>> from functools import wraps, singledispatchmethod
        >>> from dstk.metrics import Aggregator
        >>> 
        >>> class MonAggregator(Aggregator):
        >>>     "docstring de la classe"
        >>> 
        >>>     # Important : redéfinir la méthode make_message en la décorant
        >>>     # de singledispatchmethod et qui renvoit vers le make_message
        >>>     # de la classe mère
        >>>     @singledispatchmethod
        >>>     def make_message(self, input):
        >>>         return super().make_message(input)
        >>> 
        >>>     # Ajout d'un agrégateur pour le type MonObj
        >>>     @make_message.register
        >>>     def _(self, input: MonObj):
        >>>         return dict(type='MonObj', out=input.out)
        >>> 
        >>>     # Surchage du type list
        >>>     @make_message.register
        >>>     def _(self, input: list):
        >>>         return dict(
        >>>             type = 'list',
        >>>             len = len(input),
        >>>             out = input[0]
        >>>          )
        """
        from functools import singledispatchmethod
        
        @singledispatchmethod
        def make_message(self, input):
            return dict(
                type='unknown'
            )

        @make_message.register
        def _(self, input: str):
            return dict(
                type='str',
                out=input
            )

        @make_message.register(float)
        @make_message.register(np.floating)
        @make_message.register(np.float)
        @make_message.register(int)
        @make_message.register(np.integer)
        def _(self, input):
            return dict(
                type='scalar',
                out=input
            )
    
        @make_message.register(list)
        @make_message.register(tuple)
        def _(self, input):
            if not np.isscalar(input[0]):
                return dict(
                    type='list',
                    inside=str(type(input[0])),
                    len=len(input)
                )
            else:
                if len(input) > 10:
                    return dict(
                        type='list',
                        inside='scalar',
                        len=len(input)
                    )
                else:
                    info = dict(
                        type='list',
                        len=len(input),
                        inside='scalar'
                    )
                    info.update(
                        {
                            f"out_{ii}": ss for ii, ss in enumerate(input)
                        }
                    )
                    return info
    
        @make_message.register
        def _(self, input: np.ndarray):
            return dict(
                type='array',
                mean=np.mean(input),
                std=np.std(input),
                dim=len(input.shape)
            )
    
        @make_message.register
        def _(self, input: pd.DataFrame):
            info = dict(
                type='dataframe',
                nb_row=input.shape[0],
                nb_col=input.shape[1]
            )
            info.update(
                {
                    f"{col}_mean": mean
                    for mean, col in zip(input.mean(), input.columns)
                }
            )
            info.update(
                {
                    f"{col}_std": std
                    for std, col in zip(input.std(), input.columns)
                }
            )
            return info
    
        @make_message.register
        def _(self, input: dict):
             return dict(type='dict', dict=input)
    
        @make_message.register
        def _(self, input: None):
            return dict(type="none")
else:
    from warnings import warn
    warn(
        "La classe Aggregator pour le décorateur sniffer a besoin de "
        "Python 3.8 minimum et actuellement vous tournez sur la version "
        f"{version_info.major}.{version_info.minor}. Le sniffer n'est pas "
        "inutilisable, mais il vous faudra concevoir un Aggregator."
    )
    class Aggregator:
        r"""
        Classe coquille si la version de Python est inférieure à 3.8.
        """
        def make_message(self, input):
            warn(
                "Classe Aggregator coquille (vide), la classe n'est pas "
                "implémentée."
            )
            return dict(
                type='pas de type',
                msg='Aggregator à implémenter'
            )
