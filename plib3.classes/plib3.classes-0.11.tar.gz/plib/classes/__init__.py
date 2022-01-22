#!/usr/bin/env python3
"""
Sub-Package CLASSES of Package PLIB3 -- Python Class Objects
Copyright (C) 2008-2015 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains the ``StateMachine`` class.
"""

from plib.stdlib.util import ModuleProxy

from ._defs import *

__version__ = "0.11"

excludes = ['_defs']

ModuleProxy(__name__).init_proxy(__name__, __path__, globals(), locals(),
                                 excludes=excludes)

# Now clean up our namespace
del ModuleProxy, excludes
