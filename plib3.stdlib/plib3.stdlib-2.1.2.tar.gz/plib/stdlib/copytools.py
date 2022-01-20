#!/usr/bin/env python3
"""
Module COPYTOOLS -- Tools for copying Python objects
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2022 by Peter A. Donis

This module implements copy functions for function objects
and code objects, since ``copy.copy`` in the Python standard
library just returns these objects unchanged. The functions
in this module allow copies of function and code objects to
be made with selected attributes changed, but still sharing
all other attributes.
"""

import types

from plib.stdlib.builtins import first


CODE_KEYS = (
    'argcount',
    'kwonlyargcount',
    'nlocals',
    'stacksize',
    'flags',
    'code',
    'consts',
    'names',
    'varnames',
    'filename',
    'name',
    'firstlineno',
    'lnotab'
)


def copy_code(c, **kwargs):
    invalid_key = first(key for key in kwargs if key not in CODE_KEYS)
    if invalid_key:
        raise ValueError("Invalid code object attribute: co_{}".format(invalid_key))
    return types.CodeType(*tuple(
        (kwargs.get(key) or getattr(c, 'co_{}'.format(key))) for key in CODE_KEYS
    ))


def copy_function(f, **kwargs):
    result = types.FunctionType(copy_code(f.__code__, **kwargs), f.__globals__)
    for key, value in kwargs.items():
        attrname = '__{}__'.format(key)
        if attrname in dir(result):
            setattr(result, attrname, value)
        else:
            raise ValueError("Invalid function object attribute: {}".format(attrname))
    return result
