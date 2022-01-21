from __future__ import absolute_import
from __future__ import print_function
from __future__ import division


def split_quad_in_pseudo_quads(mesh, fkey, vkey):

    if len(mesh.face_vertices(fkey)) != 4:
        return None

    a = vkey
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, b, c])
    fkey_2 = mesh.add_face([a, c, d])

    return {fkey_1: a, fkey_2: a}


def merge_pseudo_quads_in_quad(mesh, fkey_1, fkey_2):

    edge = mesh.face_adjacency_halfedge(fkey_1, fkey_2)

    if edge is None:
        return None

    a, c = edge
    b = mesh.face_vertex_descendant(fkey_2, a)
    d = mesh.face_vertex_descendant(fkey_1, c)

    mesh.delete_face(fkey_1)
    mesh.delete_face(fkey_2)

    return mesh.add_face([a, b, c, d])
