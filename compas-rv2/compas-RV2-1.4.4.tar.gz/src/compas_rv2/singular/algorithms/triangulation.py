from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.geometry import delaunay_from_points
from compas.datastructures import mesh_unweld_edges
from compas.utilities import pairwise
from compas.utilities import geometric_key

from ..datastructures import Mesh


def boundary_triangulation(outer_boundary, inner_boundaries, polyline_features=[], point_features=[], delaunay=None):
    """Generate Delaunay triangulation between a planar outer boundary and planar inner boundaries. All vertices lie the boundaries.

    Parameters
    ----------
    outer_boundary : list
        Planar outer boundary as list of vertex coordinates.
    inner_boundaries : list
        List of planar inner boundaries as lists of vertex coordinates.
    polyline_features : list
        List of planar polyline_features as lists of vertex coordinates.
    point_features : list
        List of planar point_features as lists of vertex coordinates.
    delaunay : callable or proxy
        Delaunay triangulation function.

    Returns
    -------
    delaunay_mesh : Mesh
        The Delaunay mesh.

    """
    if not delaunay:
        delaunay = delaunay_from_points

    vertices, faces = delaunay(outer_boundary, points=point_features, curves=polyline_features, holes=inner_boundaries)

    mesh = Mesh.from_vertices_and_faces(vertices, faces)

    if polyline_features:
        gkey_key = mesh.gkey_key()
        edges = [edge for polyline in polyline_features for edge in pairwise([gkey_key[geometric_key(point)] for point in polyline])]
        mesh_unweld_edges(mesh, edges)

    return mesh
