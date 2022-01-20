#!/usr/bin/env python3
"""
TEST.STDLIB.MODULEPROXY_TESTMOD.PY -- test module for ModuleProxy tests
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This is a test module for the unit tests of the ModuleProxy class.
"""

from plib.stdlib.util import ModuleProxy

test_var_static = "Static test variable."


def _test_fn():
    return "Function returning test value."


_names = {
    'test_var_dynamic': "Dynamic test variable.",
    'test_fn': _test_fn
}

ModuleProxy(__name__).init_proxy(__name__, None, globals(), locals(),
                                 names=_names, autodiscover=False)

del _test_fn, _names
