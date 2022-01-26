#!/usr/bin/python
"""
    raise_with2.py                   Nat Goodspeed
    Copyright (C) 2018               Nat Goodspeed

NRG 2018-12-20
"""

# We must import this separate module, instead of directly embedding this
# function in exc.py, because we can't catch SyntaxError in the module being
# scanned!

def raise_with(type, value, traceback):
    raise type, value, traceback
