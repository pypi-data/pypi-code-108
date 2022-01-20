#!/usr/bin/env python3
"""
Module APP -- UI Application Classes
Sub-Package UI of Package PLIB3 -- Python UI Framework
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.ui.widgets import get_toolkit_class


PApplication = get_toolkit_class('app', 'PApplication')
