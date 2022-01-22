#!/usr/bin/env python3
"""
Module SYSTOOLS -- PLIB3 System Utilities
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains information about the system on which
PLIB3 and the Python interpreter are running, and utilities
for working with that information.

variables pythonpath, plibpath, binpath, sharepath --
    contain pathnames to root python directory, plib directory,
    third-party binary directory, and third-party shared data directory
    (the latter two are where plib's scripts and example programs will
    have been installed)
"""

import sys
import os
from contextlib import contextmanager


@contextmanager
def tmp_sys_path(dirname, index=0):
    """Temporarily insert ``dirname`` into ``sys.path`` at ``index``.
    
    Typical use case is to temporarily allow imports from a non-standard
    directory.
    
    Note that the context manager will still run if given an invalid
    ``dirname``, but ``sys.path`` will be unchanged.
    """
    
    oldpath = None
    try:
        dirname = os.path.abspath(dirname)
    except (TypeError, ValueError, AttributeError):
        pass
    else:
        if os.path.isdir(dirname):
            oldpath = sys.path[:]
            sys.path.insert(index, dirname)
    try:
        yield
    finally:
        if oldpath:
            sys.path[:] = oldpath
