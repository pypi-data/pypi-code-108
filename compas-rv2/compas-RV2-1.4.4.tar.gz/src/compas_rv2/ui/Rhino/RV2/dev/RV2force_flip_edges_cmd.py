from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from functools import partial

import compas_rhino

from compas_rv2.rhino import get_scene
from compas_rv2.rhino import rv2_undo
from compas_rv2.rhino import rv2_error


__commandname__ = "RV2force_flip_edges"


def _draw_labels(form, force):
    labels = []

    dual_edges = list(force.datastructure.edges())
    primal_edges = [force.datastructure.primal_edge(dual_edge) for dual_edge in dual_edges]

    for primal, dual in zip(primal_edges, dual_edges):
        tension = form.datastructure.edge_attribute(primal, '_is_tension')
        xyz = force.datastructure.edge_midpoint(dual[0], dual[1])
        if tension:
            labels.append({'pos': xyz, 'color': (255, 0, 0), 'text': 'T'})
        else:
            labels.append({'pos': xyz, 'color': (0, 0, 255), 'text': 'C'})

    return compas_rhino.draw_labels(labels, layer=force.settings['layer'], clear=False, redraw=True)


# ==============================================================================
# Command
# ==============================================================================


@rv2_error()
@rv2_undo
def RunCommand(is_interactive):

    scene = get_scene()
    if not scene:
        return

    form = scene.get("form")[0]
    if not form:
        print("There is no ForceDiagram in the scene.")
        return

    force = scene.get("force")[0]
    if not force:
        print("There is no ForceDiagram in the scene.")
        return

    thrust = scene.get("thrust")[0]

    # temporarily hide angle deviations ----------------------------------------

    draw_dots = scene.settings['RV2']['show.angles']
    draw_vertices = force.settings['show.vertices']
    if draw_dots:
        scene.settings['RV2']['show.angles'] = False
    if draw_vertices:
        force.settings['show.vertices'] = False
    scene.update()

    # prompt -------------------------------------------------------------------

    draw_labels = partial(_draw_labels, form, force)

    guids = draw_labels()

    while True:

        edges = force.select_edges()

        if not edges:
            break

        if edges is None:
            break

        primal_edges = [force.datastructure.primal_edge(edge) for edge in edges]

        for primal in primal_edges:
            tension = form.datastructure.edge_attribute(primal, '_is_tension')
            if tension:
                form.datastructure.edge_attribute(primal, '_is_tension', False)
            else:
                form.datastructure.edge_attribute(primal, '_is_tension', True)

        compas_rhino.delete_objects(guids, purge=True)
        scene.update()
        guids = draw_labels()

    if thrust:
        thrust.settings['_is.valid'] = False

    compas_rhino.delete_objects(guids, purge=True)

    scene.settings['RV2']['show.angles'] = draw_dots
    force.settings['show.vertices'] = draw_vertices

    force.datastructure.update_angle_deviations()
    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
