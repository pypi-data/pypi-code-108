from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

import compas
import compas_rhino
import compas_rv2
from compas_rv2.rhino import rv2_error


__commandname__ = "RV2rui"


LIB = os.path.dirname(compas_rv2.__file__)
FILE = os.path.join(LIB, 'ui', 'Rhino', 'RV2', 'dev', 'RV2.rui')


@rv2_error()
def RunCommand(is_interactive):

    if not compas.WINDOWS:
        print("Only works on Windows...")
        return

    compas_rhino.toggle_toolbargroup(FILE, 'RV2')


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
