"""init.py  -- initialization routines for liontk

setup()  -- call this once, and only once, to set up
"""

from liontk.symbols import *

import liontk.tcltalk
import liontk.gui


def setup():
    """call setup routines for all modules

    Calls the setup() routines in all other modules, in the
    appropriate order, to setup liontk.
    """
    liontk.tcltalk.setup()  # must come FIRST, contacts Tcl/Tk
    liontk.gui.setup()  # issues global GUI setup commands to Tcl/Tk


