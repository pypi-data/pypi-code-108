#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonctions décoratrice permettant de réaliser une mesure.

Created on Sun Nov 22 12:29:49 2020

@author: Cyrile Delestre
"""

import logging
from functools import wraps
from typing import Union, List
from datetime import datetime as dt

from . import Aggregator
from .push import _push_logger

def timer(
    logger: Union[logging.Logger, List, None]=None,
    delta_time: bool=False,
    name: Union[bool, str]=True
):
    r"""
    Calcul de temps d'exécution d'une fonction. Empackage dans un 
    dictionnaire le nom de la fonction (name) et le temps d'éxécution de la 
    fonction en micro-secondes (dt).

    Parameters
    ----------
    logger : Union[logging.Logger, List, None]
        Logger, None ou list, si None print dans le terminal, si list 
        append dans la liste (idéalement elle doit être initialement vide) 
        sinon  utilise le logger.
    delta_time : bool
        Si True renvoit au format lisible par un humain
        (HH:MM:SS.microsecondes), si False renvoit le temps d'éxécution en 
        microsecondes.
    name : Union[bool, str]
        nom de l'identifiant de l'appellant. Si True renvoit le nom de la 
        fonction appelante, si False ne renvoit par le nom, si string 
        renvoit le string indiqué.

    Examples
    --------
    >>> import logging
    >>> from time import sleep
    >>> from dstk.metrics import timer
    >>> 
    >>> # Création du logger
    >>> logging.basicConfig(
    >>>     level = logging.INFO,
    >>>     style = '{',
    >>>     format = '{name} {message}',
    >>>     filename = 'metrics.log',
    >>>     filemode = 'w'
    >>> )
    >>> logger = logging.getLogger('metrics.python.time')
    
    Envoi vers un logger.
    
    >>> @timer(logger=logger, delta_time=True)
    >>> def function_test(a=1, b=1, sleep_time=0.5):
    >>>     r"Docstring de la fonction fonction_test"
    >>>     sleep(sleep_time)
    >>>     return a+b
    >>> 
    >>> # Envoit dans le fichier metrics.log le nom du logger + le message de 
    >>> # time, par exemple :
    >>> # metrics.python.time {"name": "function_test", "dt": "0:00:00.500830"}
    >>> function_test()
    2
    
    Envoi vers une liste (à noter que dans ce cas où delta_time est égal à 
    True alors dt est un objet datetime.timedelta et non un string) :
    
    >>> log_time = []
    >>> @timer(logger=log_time, delta_time=True)
    >>> def function_test(a=1, b=1, sleep_time=0.5):
    >>>     r"Docstring de la fonction fonction_test"
    >>>     sleep(sleep_time)
    >>>     return a+b
    >>> 
    >>> function_test()
    2
    >>> log_time
    [{"name": "function_test", "dt": 0:00:00.500830}]
    
    Affichage dans la console Python :
    
    >>> @timer(delta_time=True)
    >>> def function_test(a=1, b=1, sleep_time=0.5):
    >>>     r"Docstring de la fonction fonction_test"
    >>>     sleep(sleep_time)
    >>>     return a+b
    >>> 
    >>> function_test()
    {"name": "function_test", "dt": 0:00:00.500830}
    2

    See also
    --------
    timer_class
    """
    def decorator(fun):
        @wraps(fun)
        def wrap(*args, **kargs):
            t1 = dt.now()
            out_fun = fun(*args, **kargs)
            d_out = dt.now()-t1
            message = dict(dt=d_out if delta_time else d_out.microseconds)
            if name:
                message['name'] = (
                    name if isinstance(name, str) else fun.__name__
                )
            if not isinstance(logger, list) and delta_time:
                message['dt'] = str(message['dt'])
            _push_logger(logger, message)
            return out_fun
        return wrap
    return decorator

def timer_class(
    logger: Union[logging.Logger, List, None]=None,
    delta_time: bool=False,
    name: Union[bool, str]=True
):
    r"""
    Décorateur d'une classe. Permet de calculer le temps d'exécution de  
    chaque méthode de la classe. Empackage dans un dictionnaire le 
    nom de la méthode (name) et le temps d'éxécution de la méthode en 
    micro-seconde (dt).

    Parameters
    ----------
    logger :  Union[logging.Logger, List, None]
        Logger, None ou list, si None print dans le terminal, si list 
        append dans la liste (idéalement elle doit être initialement vide ) 
        sinon  utilise le logger.
    delta_time : bool
        Si True renvoit au format lisible par un humain
        (HH:MM:SS.microsecondes), si False renvoit le temps d'éxécution en 
        microsecondes.
    name : Union[bool, str]
        nom de l'identifiant de l'appellant. Si True renvoit le nom de la 
        fonction appelante, si False ne renvoit par le nom, si string 
        renvoit le string indiqué.

    Examples
    --------
    >>> import logging
    >>> from time import sleep
    >>> from dstk.metrics import timer_class
    >>> 
    >>> # Création du logger au format CSV avec séparateur ';'
    >>> logging.basicConfig(
    >>>     level = logging.INFO,
    >>>     style = '{',
    >>>     format = '{asctime};{name};{message}',
    >>>     filename = 'metrics.log',
    >>>     filemode = 'w'
    >>> )
    >>> logger = logging.getLogger('metrics.python.time')
    >>> 
    >>> @timer_class(logger=logger, delta_time=True)
    >>> class ClassTest:
    >>>     r"Docstring de la classe ClassTest"
    >>>     def __init__(self, a=1, b=2):
    >>>         self.a = a
    >>>         self.b = b
    >>> 
    >>>     def method_test(self):
    >>>         r"Docstring de la méthode method_test"
    >>>         sleep(1)
    >>>         return self.a + self.b
    >>> 
    >>>     def method_test_with_input(self, a=1):
    >>>         r"Docstring de la méthode method_test_with_input"
    >>>         sleep(0.5)
    >>>         return self.a + self.b + a
    >>> 
    >>>     def method_test_without_output(self, a=1):
    >>>         r"Docstring de la méthode method_test_without_output"
    >>>         sleep(0.1)
    >>>         self.c = a
    
    >>> # L'instentiation d'une classe n'envoit rien dans le logger.
    >>> test = ClassTest()
    >>> # Envoit dans le fichier metrics.log le timestamp le nom du logger + 
    >>> # le message de time, par exemple :
    >>> # 2020-04-11T09:58:13.990425;metrics.python.time;{"name": 
    >>> # "method_test_with_input", "dt": "0:00:00.500652"}
    >>> test.method_test_with_input()
    4
    
    Pour plus d'exemples voir le décorateur "timer".

    See also
    --------
    timer
    """
    def decorator(Cls):
        class WrapClass:
            def __init__(self, *args, **kargs):
                self.new_instance = Cls(*args, **kargs)
                self.__doc__ = self.new_instance.__doc__

            def __getattribute__(self, key):
                try:
                    attribute = super(WrapClass, self).__getattribute__(key)
                except AttributeError:
                    pass
                else:
                    return attribute
                attribute = self.new_instance.__getattribute__(key)
                if callable(attribute):
                    return timer(logger, delta_time, name)(attribute)
                else:
                    return attribute
    
        return WrapClass
    return decorator

def sniffer(
    logger: Union[logging.Logger, List, None]=None,
    agg: Aggregator=Aggregator(),
    name: Union[bool, str]=True
):
    r"""
    Récolte la sortie d'une fonction permettant de surveiller le comportement 
    de la fonction. Package l'information dans un dictionnaire. Ce 
    dictionnaire contient par défaut au moins le type (type) + des infos qui 
    dépendent du type.

    Parameters
    ----------
    logger : Union[logging.Logger, List, None]
        Logger, None ou list, si None print dans le terminal, si list 
        append dans la liste (idéalement elle doit être initialement vide) 
        sinon  utilise le logger.
    agg : Aggregator
        Classe :class:`~dstk.metrics._aggregator.Aggregator` qui package 
        dans un dictionnaire les informations issues de la sortie.
    name : Union[bool, str]
        nom de l'identifiant de l'appellant. Si True renvoit le nom de la 
        fonction appelante, si False ne renvoit par le nom, si string 
        renvoit le string indiqué.

    Examples
    --------
    Exemple d'envoi vers un fichier log classic :
    
    >>> import logging
    >>> from dstk.metrics import Aggregator, sniffer
    >>> 
    >>> # Création du logger
    >>> logging.basicConfig(
    >>>     level = logging.INFO,
    >>>     style = '{',
    >>>     format = '{created} {name} {message}',
    >>>     filename = 'metrics.log',
    >>>     filemode = 'w'
    >>> )
    >>> logger = logging.getLogger('metrics.python.sniffer')
    >>> 
    >>> @sniffer(logger=logger, agg=Aggregator())
    >>> def function_test(a=1, b=1):
    >>>     r"Docstring de la fonction fonction_test"
    >>>     return a+b
    >>> 
    >>> # Envoit dans le fichier metrics.log le timestamp + le nom du logger +
    >>> # le message de sniffer, par exemple :
    >>> # 1587116257.2187557 metrics.python.sniffer {"name": "function_test",
    >>> # "type": "scalar", "out": 2}
    >>> function_test()
    2
    
    Voici un deuxième exemple où on envoit la donnée dans une base SQLite3 :
    
    >>> import numpy as np
    >>> from dstk.metrics import SQLiteHandler
    >>> from dstk.data import PandasSQLite
    >>> 
    >>> # Création du logger
    >>> logging.basicConfig(
    >>>     level = logging.INFO,
    >>>     handlers = [
    >>>         SQLiteHandler(
    >>>             path_sql = 'metrics.log',
    >>>             format = ['asctime', 'name', 'message', 'threadName']
    >>>         )
    >>>     ]
    >>> )
    >>> logger = logging.getLogger('metrics.python.sniffer')
    >>> 
    >>> @sniffer(logger=logger, agg=Aggregator())
    >>> def function_test(a=500, b=10):
    >>>     r"Docstring de la fonction fonction_test"
    >>>     return np.random.rand(a, b)
    >>> 
    >>> function_test()
    array([[0.28586659, 0.68635657, 0.0214463 , ..., 0.72955093, 0.46374203,
        0.91401919],
       [0.86642687, 0.25809078, 0.05919618, ..., 0.66675736, 0.36540648,
        0.87976802],
       ...,
       [0.27390028, 0.36790765, 0.04724844, ..., 0.9266507 , 0.97582395,
        0.18682153]])
    >>> 
    >>> function_test()
    array([[0.36979266, 0.15393057, 0.4848909 , ..., 0.81696902, 0.70991454,
        0.84205372],
       [0.81409839, 0.99492684, 0.62253569, ..., 0.84153022, 0.87136116,
        0.74612971],
       ...,
       [0.17831675, 0.56979541, 0.37167904, ..., 0.01579573, 0.43899887,
        0.55057923]])
    >>> 
    >>> df = PandasSQLite("metrics.log")
    >>> with df:
    >>>     logs = df("SELECT * FROM logs;")
    >>> 
    >>> logs[['asctime', 'name', 'threadName']]
                              asctime                    name  threadName
        0  2020-04-17T12:12:48.759743  metrics.python.sniffer  MainThread
        1  2020-04-17T12:12:48.763768  metrics.python.sniffer  MainThread
    >>> logs.message
        0    {"name": "function_test", "type": "array", "mean": 0.49331038639861874,...
        1    {"name": "function_test", "type": "array", "mean": 0.4902900945580839, ...
        Name: message, dtype: object

    See also
    --------
    sniffer_class
    """
    if not isinstance(agg, Aggregator):
        raise AttributeError(
            "L'argument 'agg' doit être un objet de type Aggregator et non "
            f"de type {type(agg)}."
        )
    def decorator(fun):
        @wraps(fun)
        def wrap(*args, **kargs):
            out_fun = fun(*args, **kargs)
            message = agg.make_message(out_fun);
            if name:
                message['name'] = (
                    name if isinstance(name, str) else fun.__name__
                )
            _push_logger(logger, message)
            return out_fun
        return wrap
    return decorator

def sniffer_class(
    logger: Union[logging.Logger, List, None]=None,
    agg: Aggregator=Aggregator,
    name: Union[bool, str]=True
):
    r"""
    Décorateur d'une classe. Récolte la sortie d'une fonction permettant de 
    surveiller le comportement  de la fonction. Package l'information dans un 
    dictionnaire. Ce dictionnaire contient par défaut au moins le type (type) 
    + des infos qui dépendent du type.

    Parameters
    ----------
    logger : Union[logging.Logger, List, None]
        logger, None ou list, si None print dans le terminal, si list 
        append dans la liste (idéalement elle doit être initialement vide) 
        sinon  utilise le logger.
    agg : Aggregator
        Classe :class:`~dstk.metrics._aggregator.Aggregator` qui package dans 
        un dictionnaire les informations issues de la sortie.
    name : Union[bool, str]
        nom de l'identifiant de l'appellant. Si True renvoit le nom de la 
        fonction appelante, si False ne renvoit par le nom, si string 
        renvoit le string indiqué.

    Examples
    --------
    >>> import logging
    >>> from dstk.metrics import Aggregator, sniffer_class
    >>> 
    >>> # Création du logger au format CSV avec séparateur ';'
    >>> logging.basicConfig(
    >>>     level = logging.INFO,
    >>>     style = '{',
    >>>     format = '{asctime};{name};{message}',
    >>>     filename = 'metrics.log',
    >>>     filemode = 'w'
    >>> )
    >>> logger = logging.getLogger('metrics.python.sniffer')
    >>> 
    >>> @sniffer_class(logger=logger, agg=Aggregator())
    >>> class ClassTest:
    >>>     r"Docstring de la classe ClassTest"
    >>>     def __init__(self, a=1, b=2):
    >>>         self.a = a
    >>>         self.b = b
    >>> 
    >>>     def method_test(self):
    >>>         r"Docstring de la méthode method_test"
    >>>         return self.a + self.b
    >>> 
    >>>     def method_test_with_input(self, a=1):
    >>>         r"Docstring de la méthode method_test_with_input"
    >>>         return self.a + self.b + a
    >>> 
    >>>     def method_test_without_output(self, a=1):
    >>>         r"Docstring de la méthode method_test_without_output"
    >>>         self.c = a
    
    >>> # L'instanciation d'une classe n'envoit rien dans le logger.
    >>> test = ClassTest()
    >>> # Envoit dans le fichier metrics.log le timestamp le nom du logger + 
    >>> # le message de time, par exemple :
    >>> # 2020-04-11T09:58:13.990425;metrics.python.sniffer;{"name": 
    >>> # "method_test_with_input", "type": "scalar", "out": 4}
    >>> test.method_test_with_input()
    4
    
    Pour plus d'exemples voir le décorateur "sniffer".

    See also
    --------
    sniffer
    """
    def decorator(Cls):
        class WrapClass:
            def __init__(self, *args, **kargs):
                self.new_instance = Cls(*args, **kargs)
                self.__doc__ = self.new_instance.__doc__

            def __getattribute__(self, key):
                try:
                    attribute = super(WrapClass, self).__getattribute__(key)
                except AttributeError:
                    pass
                else:
                    return attribute
                attribute = self.new_instance.__getattribute__(key)
                if callable(attribute):
                    return sniffer(logger, agg, name)(attribute)
                else:
                    return attribute

        return WrapClass
    return decorator
