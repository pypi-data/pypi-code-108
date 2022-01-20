#!/usr/bin/env python3
"""
Module EXAMPLES -- Entry points for example programs
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains entry points for the example programs
shipped with PLIB3.STDLIB. It uses the auto-detection
facilities in the ``postinstall`` module to generate the
entry points.
"""

from plib.stdlib import postinstall


postinstall.make_entry_points(__name__, 'plib3.stdlib', 'plib.stdlib', share_root="examples")
