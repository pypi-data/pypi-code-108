#!/usr/bin/python
"""
    raise_from3.py                   Nat Goodspeed
    Copyright (C) 2018               Nat Goodspeed

NRG 2018-12-20
"""

# We must import this separate module, instead of directly embedding this
# function in exc.py, because we can't catch SyntaxError in the module being
# scanned!

def raise_from(throw, cause):
    """
    Python 3 implementation of raise_from(), which raises 'throw' from 'cause'
    leaving the consumer compatible with both Python 3 and Python 2.
    """
    raise throw from cause
