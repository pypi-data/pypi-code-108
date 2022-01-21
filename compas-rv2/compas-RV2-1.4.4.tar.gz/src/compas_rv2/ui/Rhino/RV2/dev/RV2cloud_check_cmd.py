from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_rv2.rhino import get_proxy


__commandname__ = "RV2cloud_check"


def RunCommand(is_interactive):
    p = get_proxy()
    print(p.check())


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
