#!/usr/bin/env python3
"""
Module IMP -- Import Helper Functions
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the following helper function for
importing objects:

function import_from_module -- import_module, plus a getattr call to
    retrieve the named attribute from the dotted module; the equivalent
    of ``from x.y.z import a`` (except that module ``a`` of package
    ``x.y.z`` will not be returned unless it has already been imported
    into the namespace of ``x.y.z``)

function import_from_path -- imports a module or attribute from module
    that is on a path not normally in ``sys.path``
"""

from importlib import import_module

from plib.stdlib.systools import tmp_sys_path


def import_from_module(modname, attrname):
    """Return the module attribute pointed to by ``from x.y.z import a``.
    """
    return getattr(import_module(modname), attrname)


def import_from_path(path, modname, attrname=None):
    with tmp_sys_path(path):
        if attrname is not None:
            return import_from_module(modname, attrname)
        return import_module(modname)
