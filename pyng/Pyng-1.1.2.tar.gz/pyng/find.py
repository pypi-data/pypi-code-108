#!/usr/bin/python
"""\
@file   find.py
@author Nat Goodspeed
@date   2019-01-10
@brief  Utilities for searching sequences

Copyright (c) 2019, Nat Goodspeed
"""

from .exc import uncapture

def exactly_one(sequence, error):
    """
    Check that 'sequence' contains exactly one item. If so, return it.

    Otherwise behave according to 'error'. If it's an Exception subclass
    instance, raise it; else return it.

    This function is most powerful when passed a generator comprehension with
    a filter condition, e.g.:

    found = exactly_one(k for k,v in somedict.items() if v == 'important',
                        Error('There Can Be Only One in %s' % somedict))
    """
    # Capture sequence, which might be a generator, into a tuple.
    results = tuple(sequence)
    return results[0] if len(results) == 1 else uncapture(error)

def at_most_one(sequence, error, **kwds):
    """
    If 'sequence' contains exactly one item, return it.

    If 'sequence' is empty, return the value of keyword-only argument
    'default' (default None).

    Otherwise behave according to 'error'. If it's an Exception subclass
    instance, raise it; else return it.

    This function is most powerful when passed a generator comprehension with
    a filter condition, e.g.:

    found = at_most_one(k for k,v in somedict.items() if v == 'important',
                        Error('Ambiguous blobs in %s' % somedict))
    """
    # Capture sequence, which might be a generator, into a tuple.
    results = tuple(sequence)
    # empty sequence returns default value
    if not results:
        return kwds.get('default')
    # multiple items produce error
    if len(results) != 1:
        return uncapture(error)
    # exactly one, good
    return results[0]
