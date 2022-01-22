#!/usr/bin/env python3
"""
Module OSTOOLS -- PLIB3 Operating System Utilities
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains utilities similar to those provided
in the standard library ``os`` module.

Utility functions currently provided:

tmp_chdir -- context manager that changes to a given directory
    temporarily, then changes back to the old current directory
    when it exits.

locate -- generator that yields all filenames starting at a
    root location (by default, the current directory) that match
    a given pattern.

subdirs -- generator that yields all subdirectories of the
    given path (by default, the current directory).

dirfinder -- generator that yields all directories starting at a
    root location (by default, the current directory) that have
    a subdirectory whose name is in a given set of names.

filefinder -- generator that yields all directories starting at a
    root location (by default, the current directory) that contain
    a file whose name is in a given set of names.

data_changed -- checks if data is changed from file data at path.
    Data comparison is done as binary (sequence of bytes).
"""

import os
import fnmatch
from contextlib import contextmanager


@contextmanager
def tmp_chdir(newdir, create=False):
    oldcwd = os.getcwd()
    if create and not os.path.isdir(newdir):
        os.makedirs(newdir)
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(oldcwd)


def _gen_names(path, seq, pattern):
    for name in (os.path.abspath(os.path.join(path, item))
                 for item in seq if fnmatch.fnmatch(item, pattern)):
        yield name


def locate(pattern, root=None, include_dirs=False):
    """
    Generates all filenames in the directory tree starting at
    root that match pattern. Does not include subdirectories by
    default; this can be overridden with the include_dirs
    parameter. If subdirectories are included, they are yielded
    before regular files in the same directory.
    """
    
    root = root or os.getcwd()
    for path, dirs, files in os.walk(root):
        if include_dirs:
            for name in _gen_names(path, dirs, pattern):
                yield name
        for name in _gen_names(path, files, pattern):
            yield name


def subdirs(path=None, fullpath=False, include_hidden=False):
    """Generate subdirectories of path.
    
    The ``fullpath`` parameter determines whether the
    full pathname is returned for each subdir; it defaults
    to not doing so (i.e., just returning the bare subdir
    name).
    
    The ``include_hidden`` parameter determines whether
    hidden subdirectories (those beginning with a dot .) are
    included; the default is not to include them.
    """
    
    path = path or os.getcwd()
    for entry in os.listdir(path):
        subpath = os.path.join(path, entry)
        if os.path.isdir(subpath):
            if include_hidden or not entry.startswith('.'):
                yield (entry, subpath)[fullpath]


def dirfinder(subdirnames, path=None, recurse=False, include_hidden=False):
    """Generate all paths in tree rooted at path with a subdir in subdirnames.
    
    This is a much faster substitute for os.walk for cases where all we
    want is a list of directories matching a spec (i.e., we don't need
    to look at individual files). Testing shows a speedup of 30-50%.
    
    The default is not to recurse further into a subtree once a path is
    found with a matching subdir; the ``recurse`` parameter controls this
    behavior.
    
    The ``include_hidden`` parameter determines whether hidden
    subdirectories (those beginning with a dot .) are included in the
    search; the default is not to include them. Note that if any subdir
    names in ``subdirnames`` are hidden, matches for them will not be
    found unless this parameter is true.
    """
    
    path = path or os.getcwd()
    subdirnames = set(subdirnames)
    subpaths = set(subdirs(path, include_hidden=include_hidden))
    match = (subpaths & subdirnames)
    if match:
        yield path
    if recurse or (not match):
        for subpath in subpaths:
            for found in dirfinder(subdirnames, os.path.join(path, subpath),
                                   recurse=recurse, include_hidden=include_hidden):
                yield found


def filefinder(filenames, path=None, recurse=False, include_hidden=False):
    """Generate all paths in tree rooted at path containing a file in filenames.
    
    This is a much faster substitute for os.walk for cases where all we
    want is a list of directories matching a spec (i.e., we don't need
    to look at every individual file).
    
    The default is not to recurse further into a subtree once a path is
    found with a matching file; the ``recurse`` parameter controls this
    behavior.
    
    The ``include_hidden`` parameter determines whether hidden
    subdirectories (those beginning with a dot .) are included in the
    search; the default is not to include them. Note that hidden files
    will be found, if present, regardless of this parameter.
    """
    
    path = path or os.getcwd()
    filenames = set(filenames)
    match = any(os.path.isfile(os.path.join(path, fname)) for fname in filenames)
    if match:
        yield path
    if recurse or (not match):
        for subpath in subdirs(path, include_hidden=include_hidden):
            for found in filefinder(filenames, os.path.join(path, subpath),
                                    recurse=recurse, include_hidden=include_hidden):
                yield found


def data_changed(data, path):
    """Check if ``data`` is changed from the file data at ``path``.
    """
    
    if (not os.path.isfile(path)) or (os.stat(path).st_size != len(data)):
        return True
    with open(path, 'rb') as f:
        olddata = f.read()
    return data != olddata
