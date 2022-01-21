from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
from compas_rhino.utilities import is_curve_line
from compas_rhino.ui import CommandMenu
from compas_rv2.rhino import get_scene
from compas_rv2.datastructures import Skeleton
from compas_rv2.datastructures import Pattern
from compas_rv2.rhino import SkeletonObject
from compas_rv2.rhino import rv2_undo
from compas_rv2.rhino import rv2_error


__commandname__ = "RV2pattern_from_skeleton"


def skeleton_move_skeleton_vertex(skeletonobject):
    skeletonobject.move_skeleton_vertex()


def skeleton_move_mesh_vertex(skeletonobject):
    skeletonobject.move_mesh_vertex()


def skeleton_dynamic_draw_nodewidth(skeletonobject):
    skeletonobject.dynamic_draw_width('node_width')


def skeleton_dynamic_draw_leafwidth(skeletonobject):
    skeletonobject.dynamic_draw_width('leaf_width')


def skeleton_dynamic_draw_leafextend(skeletonobject):
    skeletonobject.dynamic_draw_width('leaf_extend')


def skeleton_add_lines(skeletonobject):
    if skeletonobject.skeleton.skeleton_branches:
        skeletonobject.add_lines()
    else:
        print("cannot add lines to a dome skeleton!")
        return


def skeleton_remove_lines(skeletonobject):
    if skeletonobject.skeleton.skeleton_branches:
        skeletonobject.remove_lines()
    else:
        print("no lines to be removed!")
        return


def skeleton_subdivide(skeletonobject):
    skeletonobject.skeleton_subdivide()


def skeleton_merge(skeletonobject):
    skeletonobject.skeleton_merge()


config = {
    "name": "modify",
    "message": "Modify",
    "options": [
        {
            "name": "Finish",
            "message": "Finish",
            "action": None
        },
        {
            "name": "MoveSkeletonVertices",
            "message": "Move_Skeleton_Vertices",
            "action": skeleton_move_skeleton_vertex
        },
        {
            "name": "MoveCoarseMeshVertices",
            "message": "Move_Coarse_Mesh_Corner_Vertices",
            "action": skeleton_move_mesh_vertex
        },
        {
            "name": "NodeWidth",
            "message": "Node_Width",
            "action": skeleton_dynamic_draw_nodewidth
        },
        {
            "name": "LeafWidth",
            "message": "Leaf_Width",
            "action": skeleton_dynamic_draw_leafwidth
        },
        {
            "name": "LeafExtend",
            "message": "Leaf_Extend",
            "action": skeleton_dynamic_draw_leafextend
        },
        {
            "name": "AddLines",
            "message": "Add_Lines",
            "action": skeleton_add_lines
        },
        {
            "name": "RemoveLines",
            "message": "Remove_Lines",
            "action": skeleton_remove_lines
        },
        {
            "name": "Subdivide",
            "message": "Subdivide",
            "action": skeleton_subdivide
        },
        {
            "name": "Merge",
            "message": "Merge",
            "action": skeleton_merge
        }
    ]
}


@rv2_error()
@rv2_undo
def RunCommand(is_interactive):
    scene = get_scene()
    if not scene:
        return

    # skeleton from single point or a set of lines
    guids_temp = compas_rhino.rs.GetObjects(
        message="Select a single point or a group of lines",
        filter=compas_rhino.rs.filter.point | compas_rhino.rs.filter.curve
        )

    if not guids_temp:
        return

    # detect input object type
    guids_points = []
    guids_lines = []
    for guid in guids_temp:
        if is_curve_line(guid):
            guids_lines.append(guid)

        if compas_rhino.rs.IsPoint(guid):
            guids_points.append(guid)

    if len(guids_points) == 1 and len(guids_lines) == 0:
        guids = guids_points
        point = compas_rhino.get_point_coordinates(guids)[0]
        skeleton = Skeleton.from_center_point(point)

    elif len(guids_points) == 0 and len(guids_lines) > 0:
        guids = guids_lines
        lines = compas_rhino.get_line_coordinates(guids)
        skeleton = Skeleton.from_skeleton_lines(lines)

    if not skeleton:
        return

    compas_rhino.rs.HideObjects(guids)
    skeletonobject = SkeletonObject(skeleton)
    skeletonobject.draw()
    skeletonobject.dynamic_draw_widths()

    compas_rhino.rs.EnableRedraw(True)

    # modify skeleton
    while True:
        menu = CommandMenu(config)
        action = menu.select_action()
        if not action:
            break

        if action['name'] == 'Finish':
            break

        action['action'](skeletonobject)
        skeletonobject.draw()

    # make pattern
    mesh = skeletonobject.skeleton.to_mesh()
    xyz = mesh.vertices_attributes('xyz')
    faces = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
    pattern = Pattern.from_vertices_and_faces(xyz, faces)

    # clear skeleton
    layer = skeletonobject.settings['layer']
    skeletonobject.clear()
    compas_rhino.delete_layers([layer])

    scene.clear()
    scene.add(pattern, name='pattern')
    scene.update()

    print("Pattern object successfully created. Input lines have been hidden.")


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    RunCommand(True)
