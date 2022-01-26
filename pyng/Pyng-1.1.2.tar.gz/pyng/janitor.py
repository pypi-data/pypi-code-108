#!/usr/bin/python
"""\
@file   janitor.py
@author Nat Goodspeed
@date   2011-09-14
@brief  Janitor class to clean up arbitrary resources

Copyright (c) 2011, Nat Goodspeed
"""

from __future__ import print_function

from collections import namedtuple
from functools import partial
import itertools
from pyng.exc import describe
import sys

class Error(Exception):
    pass

class _Dummy(object):
    """
    No-op file-like output-only object that discards everything written.
    """
    def write(self, data):
        pass

    def flush(self):
        pass

class Janitor(object):
    """
    Janitor provides a uniform way to deal with the possibility of exceptions
    in a function that acquires more and more temporary resources as it
    proceeds. While it's possible to structure such a function as:

    first = acquire()
    try:
        # ...
        second = acquire()
        try:
            # ...
            third = acquire()
            try:
                # ...
            finally:
                third.release()
        finally:
            second.release()
    finally:
        first.release()

    the extra indentation obscures the business logic, and (given finite
    screen width) makes it harder to read later code passages.

    Janitor 'flattens' the logic:

    with Janitor() as janitor:
        first = acquire()
        janitor.cleanup(first.release)
        # ...
        second = acquire()
        janitor.cleanup(second.release)
        # ...
        third = acquire()
        janitor.cleanup(third.release)
        # ...

    An exception that occurs anywhere in the body of the 'with' block will
    cause that Janitor instance to clean up exactly the resources that have
    been acquired to that point. On successful completion of the 'with' block,
    all temporary resources are cleaned up.

    Resources are cleaned up in reverse order of acquisition, just as in the
    try/finally nesting illustrated above.

    Moreover, Janitor also supports atomicity. A function that must produce
    multiple side effects if successful -- or none at all on failure -- can
    use Janitor as follows:

    with Janitor() as janitor:
        first = create()
        janitor.rollback(first.destroy)
        # ...
        second = create()
        janitor.rollback(second.destroy)
        # ...

    If the second create() (or anything after janitor.rollback(first.destroy))
    raises an exception, first.destroy() is called, and so forth.

    cleanup() and rollback() calls may be intermingled. An action passed to
    cleanup() is performed unconditionally; an action passed to rollback() is
    performed only on exception. The appropriate actions are still performed
    in strict reverse order:

    with Janitor() as janitor:
        janitor.cleanup(print, 'first')
        janitor.rollback(print, 'second')
        janitor.cleanup(print, 'third')
        raise RuntimeError('stop')

    prints:

    third
    second
    first

    Without the exception:

    with Janitor() as janitor:
        janitor.cleanup(print, 'first')
        janitor.rollback(print, 'second')
        janitor.cleanup(print, 'third')

    prints:

    third
    first

    Usage:

    Context Manager:
    with Janitor(sys.stdout) as janitor: # report cleanup actions on stdout
        ...
        janitor.cleanup(shutil.rmtree, some_temp_directory)
        ...
        janitor.rollback(os.remove, candidatefile)
        ...
    # exiting 'with' block normally performs cleanup() actions;
    # exiting with an exception performs cleanup() and rollback() actions

    Passing a file-like output stream to Janitor's constructor causes it to
    report its actions to that stream.

    Passing a _desc='description string' keyword parameter to either cleanup()
    or rollback() causes Janitor to report the operation in question using
    that 'description string'. Otherwise it attempts to deduce the function
    name. The underscore on _desc is to permit passing a desc= keyword
    parameter to a cleanup action.

    A Janitor instance is reusable. Thus it may be stored as an instance
    attribute of a class object and shared among methods of that class; the
    top-level entry point can write 'with self.janitor:' and control the final
    cleanup.

    Moreover, the same Janitor instance (e.g. an instance attribute) may be
    reused in nested 'with' statements (e.g. in that object's methods).
    Exiting each 'with' block only performs cleanup actions (whether cleanup()
    or rollback()) registered within or below that 'with' block, according to
    how that particular 'with' block is exited.

    Test Class:
    class TestMySoftware(unittest.TestCase, Janitor):
        def __init__(self):
            Janitor.__init__(self)  # quiet cleanup
            ...

        def setUp(self):
            ...
            self.cleanup(os.rename, saved_file, original_location)
            ...

        def tearDown(self):
            Janitor.tearDown(self)  # calls done()
            ...
            # Or, if you have no other tearDown() logic for
            # TestMySoftware, you can omit the TestMySoftware.tearDown()
            # def entirely and let it inherit Janitor.tearDown().

    Note that outside a 'with' block, Janitor cannot distinguish between
    successful completion and exception -- so in that case it does not honor
    rollback(). In fact, calling rollback() on a Janitor instance not used as
    a context manager raises Error. This is deemed safer than silently
    ignoring rollback() calls.
    """
    triple = namedtuple('triple', ('always', 'desc', 'func'))
    
    def __init__(self, report=None, errors=sys.stderr):
        """
        If you pass report= (e.g.) sys.stdout or sys.stderr, Janitor will
        report its cleanup operations as it performs them. If you don't, it
        will perform them quietly -- unless one or more of the actions throws
        an exception, in which case you'll get output on the stream passed as
        errors.
        """
        self.report  = report or _Dummy()
        self.errors  = errors
        self.actions = []
        self.with_depth = []

    def cleanup(self, func, *args, **kwds):
        """
        Unconditionally call func(*args, **kwds) at done() time.

        Pass the callable you want to call at done() time, plus any
        positional or keyword args you want to pass it.

        Pass keyword-only _desc='description' to describe the cleanup action
        as 'description' instead of as 'func(args, kwds)'.
        """
        self._add(True, func, *args, **kwds)

    def rollback(self, func, *args, **kwds):
        """
        Call func(*args, **kwds) only if we leave with an exception.

        Pass keyword-only _desc='description' to describe the cleanup action
        as 'description' instead of as 'func(args, kwds)'.

        Calling this outside a 'with' block raises Error.
        """
        if not self.with_depth:
            raise Error("Calling Janitor.rollback() outside a 'with' block is an error")

        self._add(False, func, *args, **kwds)

    def _add(self, always, func, *args, **kwds):
        # Support a keyword-only desc= parameter for both cleanup() and rollback()
        try:
            desc = kwds.pop('_desc')
        except KeyError:
            # Caller didn't pass _desc= keyword parameter.
            # Get a name string for 'func'.
            try:
                # A free function has a __name__
                name = func.__name__
            except AttributeError:
                try:
                    # A class object (even builtin objects like ints!) support
                    # __class__.__name__
                    name = func.__class__.__name__
                except AttributeError:
                    # Shrug! Just use repr() to get a string describing this func.
                    name = repr(func)
            # Construct a description of this operation in Python syntax from
            # args, kwds.
            desc = "{}({})".format(name, ", ".join(itertools.chain((repr(a) for a in args),
                                                                   (u"{}={!r}".format(k, v)
                                                                    for (k, v) in kwds.items()))))

        # Use functools.partial() to bind passed args and keywords to the
        # passed func so we get a nullary callable that does what caller
        # wants.
        self.actions.append(self.triple(always=always, desc=desc,
                                        func=partial(func, *args, **kwds)))

    def __enter__(self):
        # remember how many actions were already in our list at entry to this
        # 'with' block
        self.with_depth.append(len(self.actions))
        return self

    def __exit__(self, type, value, tb):
        # recall how many pre-existing actions were on our list at entry to
        # this level of 'with' block; only perform what we've added since then
        backto = self.with_depth.pop(-1)
        # Perform cleanup no matter how we exit this 'with' statement
        self.done(_exc=type is not None, _backto=backto)
        # Propagate any exception from the 'with' statement, don't swallow it
        return False

    def done(self, _exc=False, _backto=0):
        """
        Perform all the actions saved with cleanup() calls (since _backto). If
        _exc, perform rollback() actions along the way too.
        """
        # Snip off the tail of self.actions added since _backto.
        actions = self.actions[_backto:]
        del self.actions[_backto:]
        # Typically one allocates resource A, then allocates resource B that
        # depends on it. In such a scenario it's appropriate to delete B
        # before A -- so perform cleanup actions in reverse order. (This is
        # the same strategy used by atexit().)
        while actions:
            # Until our list is empty, pop the last triple.
            triple = actions.pop(-1)

            # cleanup() actions are always performed.
            # rollback() actions are performed only when we hit an exception.
            if not (triple.always or _exc):
                continue

            # If requested, report the action.
            print(triple.desc, file=self.report)

            try:
                # Call the bound callable
                triple.func()
            except Exception as err:
                # This is cleanup. Report the problem but continue.
                print("Calling {}\nraised  {}".format(triple.desc, describe(err)),
                      file=self.errors)

    def tearDown(self):
        """
        If a unittest.TestCase subclass (or a nose test class) adds Janitor as
        one of its base classes, and has no other tearDown() logic, let it
        inherit Janitor.tearDown().
        """
        self.done()
