from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas_rv2.singular.rhino import automated_smoothing_surface_constraints
from compas_rv2.singular.rhino import automated_smoothing_constraints
from compas_rv2.singular.rhino import constrained_smoothing
from compas_rv2.singular.rhino import RhinoPoint
from compas_rv2.singular.rhino import RhinoSurface
from compas_rv2.singular.rhino import RhinoCurve

from compas_rv2.datastructures import Pattern
from compas_rv2.rhino import get_scene
from compas_rv2.rhino import get_proxy
from compas_rv2.rhino import rv2_undo
from compas_rv2.rhino import rv2_error


__comrv2mandname__ = "RV2pattern_from_features"


@rv2_error()
@rv2_undo
def RunCommand(is_interactive):
    scene = get_scene()
    if not scene:
        return

    proxy = get_proxy()
    if not proxy:
        return

    delaunay = proxy.function('compas_cgal.triangulation.constrained_delaunay_triangulation')

    # Get input data.
    surf_guid = compas_rhino.select_surface("Select a surface to decompose.")
    if not surf_guid:
        return

    point_guids = compas_rhino.select_points("Select points to include in the decomposition.")
    # point_guids = []
    curve_guids = []

    surface = RhinoSurface.from_guid(surf_guid)
    curves = [RhinoCurve.from_guid(guid) for guid in curve_guids]
    points = [RhinoPoint.from_guid(guid) for guid in point_guids]

    # Compute the feature discretisation length.
    box = compas_rhino.rs.BoundingBox([surf_guid])
    diagonal = compas_rhino.rs.Distance(box[0], box[6])
    D = 0.05 * diagonal

    # Get the target length for the final quad mesh.
    L = compas_rhino.rs.GetReal("Define the target edge length of the pattern.", 1.0)

    compas_rhino.rs.HideObjects([surf_guid] + point_guids + curve_guids)

    # Generate the pattern
    pattern = Pattern.from_surface_and_features(D, L, surf_guid, curve_guids, point_guids, delaunay=delaunay)

    scene.clear()
    scene.add(pattern, name='pattern')
    scene.update()

    kmax = 10

    # Constrain mesh components to the feature geometry.
    constraints = automated_smoothing_surface_constraints(pattern, surface)
    constraints.update(
        automated_smoothing_constraints(pattern, rhinopoints=points, rhinocurves=curves)
    )

    while True:
        option = compas_rhino.rs.GetString("Smoothen the pattern?", "No", ["Yes", "No"])
        if not option:
            break
        if option != "Yes":
            break

        constrained_smoothing(
            pattern, kmax=kmax, damping=0.5, constraints=constraints, algorithm="area"
        )
        scene.update()

    print('Pattern object successfully created. Input object has been hidden.')


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
