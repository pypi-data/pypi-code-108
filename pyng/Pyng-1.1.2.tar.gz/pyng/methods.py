#!/usr/bin/env python
"""
    methods.py                       Nat Goodspeed
    Copyright (C) 2019               Nat Goodspeed

NRG 2019-01-21
"""

from builtins import str
from builtins import object
from functools import partial
import sys

class Error(Exception):
    pass

# TODO: This should be implemented in terms of descriptors.
# - Decorate a cached *method* using @single_cached or @multi_cached.
# - Decorator replaces the method with a descriptor class Cacher.
# - Cacher.__init__(method) stores the original method.
# - Cacher.__get__(self, instance, cls) returns a (possibly new) ...
raise NotImplementedError("""Entirely moot: see functools.lru_cache()
(functools32 package for Python 2)""")

# Instantiate a distinct object we can use to mean: no cached result yet.
# Avoid None, since None might be a legitimate return value from a cached
# method.
_UNSET = object()

class single_cached_method(object):
    """
    single_cached_method is a class decorator that wraps the method named by
    'get' with logic that calls it only once, caching its return value in a
    hidden attribute. Thereafter, calls to the wrapper return that same value
    -- regardless of the passed arguments. See also multi_cached_method.

    If the original 'get' method raises an exception, each subsequent call to
    the wrapper will re-raise that same exception.

    You may optionally specify a 'set' method name as well. If you do,
    single_cached_method injects a method by that name.

    Calling the 'set' method with a new value updates the stored value;
    thereafter calls to the 'get' method will return the updated value. Of
    course, calling 'set' before the first call to 'get' ensures that the
    original 'get' method won't be called.

    Calling the 'set' method with no argument invalidates any previously-
    stored value, so that the next call to 'get' will in fact call the
    original 'get' method.

    You may optionally specify an 'unset' method name. If you do,
    single_cached_method injects a nullary method by that name. This has the
    same effect as calling a 'set' method with no argument: it invalidates the
    cache.

    'get' is a string naming the method whose result you want to cache.

    'set' is an optional string naming the 'set' method to generate. If you
          omit it, no 'set' method is injected.

    'unset' is an optional string naming the 'unset' method to generate. If
            you omit it, no 'unset' method is injected.
    """
    # For decorators accepting arguments, I like to use a class with a
    # __call__() method. That separates out the functionality into an
    # __init__() method that accepts and stores the arguments, versus the
    # __call__() method that receives and decorates the function or class of
    # interest. This seems clearer to me than a function defining and
    # returning a function which, in turn, defines and returns a wrapper...
    def __init__(self, get, set=None, unset=None):
        self.getname = get
        self.setname = set
        self.unsetname = unset
        # Generate an attribute name. The leading double underscore convention
        # should hopefully make the attribute class-local. We could add some
        # fuzz for uniqueness if necessary.
        # Bake in the method name so that a given class can use this decorator
        # for more than one method.
        self.varname = '__{}_getter'.format(get)

    def __call__(self, cls):
        # Do NOT specify a default: if self.getname doesn't actually name a
        # method defined on cls, it's an error.
        self.oldget  = getattr(cls, self.getname)
        self.oldinit = cls.__init__

        # replace cls constructor with our init()
        cls.__init__ = self.init
        # replace getname with our get()
        setattr(cls, self.getname, self.get)

        # if setter was specified, inject our set() with that name
        if self.setname:
            setattr(cls, self.setname, self.set)

        # same for unsetname
        if self.unsetname:
            setattr(cls, self.unsetname, self.unset)

        # we just modified cls, we didn't replace it
        return cls

    def init(self, instance, *args, **kwds):
        # Initialize the cache attribute FIRST, because the real constructor
        # may well choose to store an intended cache value.
        setattr(instance, self.varname, self.caller)
        # Now call the real constructor.
        self.oldinit(instance, *args, **kwds)

    def get(self, instance, *args, **kwds):
        # dispatch this call through self.varname
        return getattr(instance, self.varname)(instance, *args, **kwds)

    def caller(self, instance, *args, **kwds):
        # This is reached for the first call, or the next call after an
        # unset() call.
        try:
            result = self.oldget(instance, *args, **kwds)
        except Exception as err:
            # capture this exception for future calls
            setattr(instance, self.varname, partial(self.raiser, err))
            raise
        else:
            # capture return value for future calls
            setattr(instance, self.varname, lambda *args, **kwds: result)
            return result

    def raiser(exc, *args, **kwds):
        raise exc

    def set(self, instance, value=_UNSET):
        # If value is omitted, reinitialize self.varname so that the next call
        # is passed through by our self.caller().
        # If value is passed, set self.varname so the next call will return
        # that value.
        setattr(instance, self.varname,
                self.caller if value is _UNSET else lambda *args, **kwds: value)

    def unset(self, instance):
        # This method is really for consistency with multi_cached_method.
        setattr(instance, self.varname, self.caller)

class multi_cached_method(object):
    """
    multi_cached_method is a class decorator that wraps the method named by
    'get' with logic that calls it only once for a particular set of
    arguments, caching its return value in a hidden attribute. Thereafter, any
    call to the wrapper with the same set of arguments will return that same
    value. See also single_cached_method.

    Limitation: multi_cached_method attempts to store the positional and
    keyword arguments you pass as the composite key of a dict whose value is
    the return value for that set of arguments. Therefore, multi_cached_method
    can only support methods whose argument types can be used in a dict key.

    Limitation: multi_cached_method doesn't actually resolve positional or
    keyword arguments into the target method's argument list. The cached value
    from a previous call will be returned only if you pass each argument the
    same way as before. That is, if an argument previously passed as
    positional is next passed as a keyword, the target method will be called
    again with the new arguments.

    You may optionally specify a 'set' method name as well. If you do,
    multi_cached_method injects a method by that name. That method accepts a
    value, plus the positional and keyword arguments for which that value
    should be returned.

    Thereafter, calls to the 'get' method with those arguments will return the
    updated value. Of course, calling 'set' before the first call to 'get'
    ensures that the original 'get' method won't be called.

    You may optionally specify an 'unset' method name. If you do,
    multi_cached_method injects a method by that name. Calling the 'unset'
    method with a particular set of arguments invalidates the value cached for
    that set of arguments. A subsequent call to the 'get' wrapper with that
    set of arguments will be forwarded to the original 'get' method.

    'get' is a string naming the method whose result you want to cache.

    'set' is an optional string naming the 'set' method to generate. If you
          omit it, no 'set' method is injected.

    'unset' is an optional string naming the 'unset' method to generate. If
            you omit it, no 'unset' method is injected.
    """
    def __init__(self, get, set=None, unset=None):
        raise NotImplementedError("multi_cached_method not yet done")

def main():
    pass

if __name__ == "__main__":
    try:
        sys.exit(main(*sys.argv[1:]))
    except Error as err:
        sys.exit(str(err))
