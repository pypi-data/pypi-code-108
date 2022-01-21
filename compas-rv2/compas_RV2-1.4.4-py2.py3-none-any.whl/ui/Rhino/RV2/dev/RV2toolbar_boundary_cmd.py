from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_rv2.rhino import get_scene
from compas_rv2.rhino import rv2_error


import RV2boundary_supports_cmd
import RV2boundary_boundaries_cmd


__commandname__ = "RV2toolbar_boundary"


@rv2_error()
def RunCommand(is_interactive):

    scene = get_scene()
    if not scene:
        return

    pattern = scene.get("pattern")[0]
    if not pattern:
        print("There is no Pattern in the scene.")
        return

    options = ["IdentifySupports", "UpdateBoundaries"]

    while True:
        option = compas_rhino.rs.GetString("Define boundary conditions:", strings=options)
        if not option:
            return

        if option == "IdentifySupports":
            RV2boundary_supports_cmd.RunCommand(True)

        elif option == "UpdateBoundaries":
            RV2boundary_boundaries_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
