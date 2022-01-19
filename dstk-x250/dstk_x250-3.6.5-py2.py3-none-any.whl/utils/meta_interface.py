#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 11:59:50 2021

@author: cyriledelestre
"""

from abc import ABCMeta

class SuperclassDocstring(ABCMeta):
    r"""
    Méta classe permettant de faire hériter la documention d'une calsse 
    abstraite à la classe concrète.
    """
    def __new__(mcls, classname, bases, cls_dict):
        cls = ABCMeta.__new__(mcls, classname, bases, cls_dict)
        mro = cls.__mro__[1:]
        for name, member in cls_dict.items():
            if not getattr(member, '__doc__'):
                for base in mro:
                    try:
                        member.__doc__ = getattr(base, name).__doc__
                        break
                    except AttributeError:
                        pass
        return cls