from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_rv2.rhino import get_scene
from compas_rv2.rhino import rv2_error

import RV2thrust_attributes_cmd
import RV2thrust_modify_vertices_cmd
import RV2thrust_move_supports_cmd
import RV2thrust_modify_faces_cmd


__commandname__ = "RV2toolbar_modify_thrust"


@rv2_error()
def RunCommand(is_interactive):

    scene = get_scene()
    if not scene:
        return

    pattern = scene.get("thrust")[0]
    if not pattern:
        print("There is no ThrustDiagram in the scene.")
        return

    options = ["DiagramAttributes", "VerticesAttributes", "FacesAttributes", "MoveSupports"]
    option = compas_rhino.rs.GetString("Modify thrust diagram:", strings=options)

    if not option:
        return

    if option == "DiagramAttributes":
        RV2thrust_attributes_cmd.RunCommand(True)

    elif option == "VerticesAttributes":
        RV2thrust_modify_vertices_cmd.RunCommand(True)

    elif option == "FacesAttributes":
        RV2thrust_modify_faces_cmd.RunCommand(True)

    elif option == "MoveSupports":
        RV2thrust_move_supports_cmd.RunCommand(True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
