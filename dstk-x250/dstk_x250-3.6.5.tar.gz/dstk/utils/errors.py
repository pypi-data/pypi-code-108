#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toutes les classes erreurs personalisées
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Created on Thu Nov 26 12:15:33 2020

@author: Cyrile Delestre
"""

from typing import Optional

class NoConsistentError(Exception):
    r"""
    Classe d'erreur de consistance (représentation matricielle non dense).
    
    Parameters
    ----------
    msg : Optional[str]
        message à passer avec l'erreur.
    """
    def __init__(self, msg: Optional[str]=None):
        self.msg = msg

class CheckError(Exception):
    r"""
    Classe d'erreur des ckeckage.
    
    Parameters
    ----------
    msg : Optional[str]
        message à passer avec l'erreur.
    """
    def __init__(self, msg: Optional[str]=None):
        self.msg = msg

class DivergenceError(Exception):
    r"""
    Classe d'erreur de convergence.
    
    Parameters
    ----------
    msg : Optional[str]
        message à passer avec l'erreur.
    """
    def __init__(self, msg: Optional[str]=None):
        self.msg = msg

class TrainError(Exception):
    r"""
    Classe d'erreur quelconque durant l'apprentissage.
    
    Parameters
    ----------
    msg : Optional[str]
        message à passer avec l'erreur.
    """
    def __init__(self, msg: Optional[str]=None):
        self.msg = msg
