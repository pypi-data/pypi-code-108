from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
from compas_rv2.rhino import get_scene
from compas_rv2.rhino import AttributesForm
from compas_rv2.rhino import rv2_error


__commandname__ = "RV2thrust_attributes"


HERE = compas_rhino.get_document_dirname()


@rv2_error()
def RunCommand(is_interactive):

    scene = get_scene()
    if not scene:
        return

    thrust = scene.get("thrust")[0]
    if not thrust:
        print("There is no ThrustDiagram in the scene.")
        return

    AttributesForm.from_sceneNode(thrust)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
