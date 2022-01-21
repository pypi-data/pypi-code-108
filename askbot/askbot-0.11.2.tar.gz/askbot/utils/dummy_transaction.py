"""Dummy transaction module, use instead of :mod:`django.db.transaction`
when you want to debug code that would normally run under transaction management.
Usage::

    from askbot.utils import dummy_transaction as transaction

"""
import functools

def commit():
    """fake transaction commit"""
    pass
