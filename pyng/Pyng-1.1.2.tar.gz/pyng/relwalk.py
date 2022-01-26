#!/usr/bin/python
"""
    relwalk.py                       Nat Goodspeed
    Copyright (C) 2010               Nat Goodspeed

NRG 12/01/10
"""

import os
import itertools

def relwalk(base, *args, **kwds):
    """Produce os.walk triples in which the directory name is relative to the
    original base directory, rather than having the base prepended. This is
    useful for situations such as copying a directory tree, or comparing two
    trees: anything where you need to walk two trees in parallel.

    If you pass a keyword argument skipdirs=, it should be a callable
    predicate accepting the pathname (relative to base) of a subdirectory. Any
    subdirectory for which the predicate returns True will NOT be traversed.

    It's important to filter directories here at this level because you can
    prune entire subdirectory trees by interacting with os.walk(). That's not
    only more succinct but -- especially with a mounted filesystem --
    potentially very much more efficient than traversing them all and then
    filtering after the fact.

    Similarly, you may pass a keyword argument skipfiles= with a like
    predicate. This is mere convenience, since it's completely equivalent to
    filtering you could perform on the returned values.
    """
    nopfilter = lambda path: False
    # Use kwds.pop() because we do NOT want to pass either 'skipfiles=' or
    # 'skipdirs=' to os.walk()!
    skipfiles = kwds.pop("skipfiles", nopfilter)
    skipdirs  = kwds.pop("skipdirs",  nopfilter)
    for dir, dirs, files in os.walk(base, *args, **kwds):
        # The first (topdown=True) or last (topdown=False) dir produced by
        # os.walk() will be base itself. Every other triple's dir will be base
        # + os.sep + subdir path. Every single dir item SHOULD begin with base
        # -- but since we ruthlessly chop it off, it feels safer to test
        # first. Removing base from the first (last) dir will produce an
        # empty string. In every other case it will produce a string with a
        # leftmost os.sep char. lstrip() that to leave only the relative
        # subdir path.
        if dir.startswith(base):
            trimdir = dir[len(base):].lstrip(os.sep)
        else:
            # If for some strange reason os.walk() tosses us a triple whose
            # dir does NOT begin with base, better just use that.
            trimdir = dir
        # Filter out any directories for which skipdirs is true. Actually
        # remove them from 'dirs' so that os.walk will ignore them. Iterate
        # over a copy of 'dirs' so we can safely modify the original list.
        for d in dirs[:]:
            if skipdirs(os.path.join(trimdir, d)):
                dirs.remove(d)
        # Also filter out any files for which skipfiles is true.
        yield trimdir, dirs, [f for f in files if not skipfiles(os.path.join(trimdir, f))]

def relfiles(*args, **kwds):
    """Produce relative paths for all the files under a particular base
    directory, using relwalk().
    """
    for dir, dirs, files in relwalk(*args, **kwds):
        for file in files:
            yield os.path.join(dir, file)

def reldirs(*args, **kwds):
    """Produce relative paths for all the subdirectories under a particular
    base directory, using relwalk().
    """
    for dir, dirs, files in relwalk(*args, **kwds):
        for subdir in dirs:
            yield os.path.join(dir, subdir)

def relnames(*args, **kwds):
    """
    Produce relative pathnames for all the subdirectories and files under a
    particular base directory, using relwalk().
    """
    for dir, dirs, files in relwalk(*args, **kwds):
        for name in itertools.chain(dirs, files):
            yield os.path.join(dir, name)
