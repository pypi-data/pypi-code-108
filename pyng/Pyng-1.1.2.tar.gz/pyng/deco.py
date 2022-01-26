#!/usr/bin/python
"""\
@file   deco.py
@author Nat Goodspeed
@date   2020-10-29
@brief  Utility decorators

Copyright (c) 2020, Nat Goodspeed
"""

from functools import wraps
import inspect

# Kind of too bad 'with' is a keyword, else we'd use that.
# _with() seems potentially confusing.
class within(object):
    """
    Execute a function's entire body within a particular context manager.

    Usage:

    some_context_manager = ...

    @within(some_context_manager)
    def somefunc(someargs):
        # ...

    is equivalent to:

    def somefunc(someargs):
        with some_context_manager:
            # ...

    The major difference is that, for instance, in a class definition the
    latter form must qualify some_context_manager with either 'self' or the
    class name. But @within(some_context_manager) looks up
    some_context_manager while it's still in the local scope being defined, so
    needs no qualification.

    If you pass @within() a callable, it is called, and the return value is
    used as the context manager, as if:

    def somefunc(someargs):
        with some_context_manager():
            # ...

    If you pass @within() a callable and some set of positional and keyword
    arguments, it is called with those arguments:

    @within(some_context_callable, posarg, kwdarg=True)
    def somefunc(someargs):
        # ...

    is equivalent to:

    def somefunc(someargs):
        with some_context_callable(posarg, kwdarg=True):
            # ...

    Either way, if 'someargs' includes a '_context' named argument (with or
    without a default value), or includes a '**kwds' argument, the value
    returned by some_context_manager.__enter__() is passed as keyword argument
    _context. So:

    @within(some_context_manager)
    def somefunc(someargs, _context=None):
        # ... reference _context ...

    is equivalent to:

    def somefunc(someargs):
        with some_context_manager as _context:
            # ... reference _context ...
    """
    def __init__(self, ctxmgr, *args, **kwds):
        if callable(ctxmgr):
            # If ctxmgr is already callable, just store it, along with args
            # and keywords to pass through.
            self.ctxmgr = ctxmgr
            self.args   = args
            self.kwds   = kwds
        else:
            # ctxmgr isn't itself callable, so store a callable that returns
            # ctxmgr. But -- in this case it's an error to also pass (*args,
            # **kwds).
            if args or kwds:
                raise TypeError("Can't pass function arguments "
                                "with non-callable() within() argument")

            self.ctxmgr = lambda: ctxmgr
            self.args   = ()
            self.kwds   = {}

    def __call__(self, func):
        # examine func()'s signature
        argspec = inspect.getargspec(func)
        # If func() accepts either a _context named argument (with or without
        # default) or a **kwds argument, pass _context= arg on every call.
        if ('_context' in argspec.args) or argspec.keywords:
            @wraps(func)
            def decorated(*args, **kwds):
                with self.ctxmgr(*self.args, **self.kwds) as context:
                    return func(_context=context, *args, **kwds)
        else:
            @wraps(func)
            def decorated(*args, **kwds):
                with self.ctxmgr(*self.args, **self.kwds):
                    return func(*args, **kwds)
        return decorated

class DontCall(object):
    """
    The within() decorator tests whether the passed object is callable(); if
    it is, it calls it. What about a multi-purpose object which can serve as a
    context manager AND is callable()? If you really want to use the instance
    in hand rather than calling it, wrap it in DontCall before passing it to
    within():

    @within(DontCall(context_manager_instance))
    def somefunc(someargs):
        # ...
    """
    def __init__(self, target):
        self.target = target

    # This class is a simple proxy that forwards ONLY __enter__() and
    # __exit__() calls: the context manager API.
    def __enter__(self):
        return self.target.__enter__()

    def __exit__(self, *args, **kwds):
        return self.target.__exit__(*args, **kwds)
