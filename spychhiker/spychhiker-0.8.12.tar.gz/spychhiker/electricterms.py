#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 09:32:12 2020

@author: benjamin
"""

class AcousticsElem:
    """ Values of electric components of the equivalent circuit""" 
    
    parent = None
    Lj = None
    Rj = None
    Cj = None
    Gw = None
    wl = None
    wc = None
    Udj = None
    bj = None
    Hj = None
    Rcm = None
    Rcp = None
    Ns = None
    
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            
class DerivTerms:
    """ contains the derivaztive terms"""
    
    parent = None
    Q = None
    Qwl = None
    Qwc = None
    Qnc = None

    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)
            
class IntegrTerms:
    """ Contains the integration terms"""
    
    parent = None
    Vc = None
    V = None
    
    def __init__(self, *args):
        nargin = len(args)
        for k in range(0, nargin, 2):
            key, value = args[k:k+2]
            setattr(self, key, value)