#!/usr/bin/env python3
"""
Module BUILTINS -- PLIB3 Extensions to the Python Built-Ins
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module adds some functions to the Python builtin
namespace. Importing the module is sufficient; no other
code is needed. However, the extra functions also appear
in this module's namespace, so if you want to be more
explicit about what's happening, you can say, for example,

    ``from plib.stdlib.builtins import first``

instead of

    ``import plib.stdlib.builtins``

which makes it less obvious where the function ``first``
is coming from.
"""

from ._extras import *

EXTRA_NAMES = [
    'first',
    'inverted',
    'last',
    'prod',
    'type_from_name'
]

# This ensures we don't run the upgrade multiple times
_upgraded = False


def upgrade_builtins():
    """Upgrades __builtin__ namespace with plib extra functions.
    
    Additional plib-specific "builtins":
    
    - ``first``
    - ``inverted``
    - ``last``
    - ``prod``
    - ``type_from_name``
    
    Note that we return a string indicating what, if anything,
    was done; this can be used as a diagnostic if needed.
    """
    
    global _upgraded
    if not _upgraded:
        import builtins
        from plib.stdlib import _extras
        for extra_name in EXTRA_NAMES:
            setattr(builtins, extra_name, getattr(_extras, extra_name))
        _upgraded = True
        return "Upgraded built-ins installed!"
    return "Upgrade already performed, nothing to do."


upgrade_builtins()
