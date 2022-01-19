#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Décorateurs deprecated
^^^^^^^^^^^^^^^^^^^^^^

Created on Mon Nov 23 11:29:42 2020

@author: Cyrile Delestre
"""

from functools import singledispatch, wraps
from warnings import warn

@singledispatch
def deprecated(fun, *args, **kwargs):
    """
    Décorateur indiquant que la fonction est dépréciée.
    
    Examples
    --------
    >>> from dstk.utils.deprecated import deprecated
    
    >>> @deprecated
    >>> def fun():
    >>>     print("Hello world!")
    
    >>> fun()
    :1: DeprecationWarning: La fonction fun est dépreciée !
    """
    @wraps(fun)
    def wrapper(*args, **kwargs):
        warn(
            f"La fonction {fun.__name__} est dépreciée !",
            DeprecationWarning
        )
        return fun(*args, **kwargs)
    return wrapper

@deprecated.register(str)
def _deprecated(msg: str, *args, **kwargs):
    """
    Décorateur indiquant que la fonction est dépréciée et affiche un message 
    entré par l'utilisateur.
    
    Parameters
    ----------
    msg : str
        message à transmettre dans le warning
    
    Examples
    --------
    >>> from dstk.utils.deprecated import deprecated
    
    >>> @deprecated("Fonction plus valide dans la prochaine version.")
    >>> def fun():
    >>>     print("Hello world!")
    
    >>> fun()
    :1: DeprecationWarning: La fonction fun est dépreciée !
    Fonction plus valide dans la prochaine version.
    """
    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            warn(
                f"La fonction {fun.__name__} est dépreciée !\n{msg}",
                DeprecationWarning
            )
            return fun(*args, **kwargs)
        return wrapper
    return decorator
