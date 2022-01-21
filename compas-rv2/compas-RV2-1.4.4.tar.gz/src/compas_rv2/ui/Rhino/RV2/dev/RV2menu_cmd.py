from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_rv2.rhino import MenuForm
from compas_rv2.rhino import rv2_error


__commandname__ = "RV2menu"


@rv2_error()
def RunCommand(is_interactive):

    m = MenuForm()
    m.setup()
    m.Show()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
