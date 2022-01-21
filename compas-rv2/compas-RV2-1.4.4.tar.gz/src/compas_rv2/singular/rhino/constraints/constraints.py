from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas_rhino

from compas.geometry import distance_point_point
from compas.geometry import closest_point_in_cloud
from compas.geometry import Polyline

from compas_rv2.singular.utilities import list_split

from ..geometry import RhinoSurface
from ..geometry import RhinoPoint
from ..geometry import RhinoCurve


def automated_smoothing_surface_constraints(mesh, surface):
    """Apply automatically surface-related constraints to the vertices of a mesh to smooth: kinks, boundaries and surface.

    Parameters
    ----------
    mesh : Mesh
        The mesh to apply the constraints to for smoothing.
    surface : :class:`compas_rv2.singular.rhino.RhinoSurface`
        A Rhino surface on which to constrain mesh vertices.

    Returns
    -------
    constraints : dict
        A dictionary of mesh constraints for smoothing as vertex keys pointing to point, curve or surface objects.

    """
    surface = RhinoSurface.from_guid(surface.guid)

    constraints = {}

    points = [RhinoPoint.from_guid(compas_rhino.rs.AddPoint(point)) for point in surface.kinks()]
    curves = [RhinoCurve.from_guid(guid) for guid in surface.borders(border_type=0)]

    constraints.update({vertex: surface for vertex in mesh.vertices()})

    for vertex in [vkey for bdry in mesh.vertices_on_boundaries() for vkey in bdry]:
        xyz = mesh.vertex_coordinates(vertex)
        projections = [(curve, distance_point_point(xyz, curve.closest_point(xyz))) for curve in curves]
        constraints[vertex] = min(projections, key=lambda x: x[1])[0]

    index_vertex = {index: vertex for index, vertex in enumerate([vkey for bdry in mesh.vertices_on_boundaries() for vkey in bdry])}
    boundary = [mesh.vertex_coordinates(vertex) for bdry in mesh.vertices_on_boundaries() for vertex in bdry]
    constraints.update({index_vertex[closest_point_in_cloud(point.xyz, boundary)[2]]: point for point in points})

    return constraints


def automated_smoothing_constraints(mesh, rhinopoints=None, rhinocurves=None, rhinosurface=None, rhinomesh=None):
    """Apply automatically point, curve and surface constraints to the vertices of a mesh to smooth.

    Parameters
    ----------
    mesh : Mesh
        The mesh to apply the constraints to for smoothing.
    rhinopoints : list
        List of XYZ coordinates on which to constrain mesh vertices.
        Default is None.
    rhinocurves : list of :class:`compas_rv2.singular.rhino.RhinoCurve`, optional
        List of Rhino curves on which to constrain mesh vertices.
        Default is None.
    rhinosurface : :class:`compas_rv2.singular.rhino.RhinoSurface`, optional
        A Rhino surface guid on which to constrain mesh vertices.
        Default is None.
    rhinomesh : :class:`compas_rv2.singular.rhino.RhinoCurve`, optional
        A Rhino mesh guid on which to constrain mesh vertices.
        Default is None.

    Returns
    -------
    constraints : dict
        A dictionary of mesh constraints for smoothing as vertex keys pointing to point, curve or surface objects.

    """
    constraints = {}
    constrained_vertices = {}

    vertices = list(mesh.vertices())
    cloud = [mesh.vertex_coordinates(vertex) for vertex in mesh.vertices()]

    if rhinopoints:
        constrained_vertices.update({vertices[closest_point_in_cloud(point.xyz, cloud)[2]]: point for point in rhinopoints})

    if rhinomesh:
        constraints.update({vertex: rhinomesh for vertex in mesh.vertices()})

    if rhinosurface:
        constraints.update({vertex: rhinosurface for vertex in mesh.vertices()})

    if rhinocurves:
        boundaries = [
            split_boundary for boundary in mesh.boundaries()
            for split_boundary in list_split(boundary, [boundary.index(vertex) for vertex in constrained_vertices.keys() if vertex in boundary])]

        boundary_polylines = [Polyline([mesh.vertex_coordinates(vertex) for vertex in boundary]) for boundary in boundaries]
        boundary_midpoints = [polyline.point(t=0.5) for polyline in boundary_polylines]
        curve_midpoints = [compas_rhino.rs.EvaluateCurve(curve.guid, compas_rhino.rs.CurveParameter(curve.guid, 0.5)) for curve in rhinocurves]

        midpoint_map = {index: closest_point_in_cloud(boundary_midpoint, curve_midpoints)[2] for index, boundary_midpoint in enumerate(boundary_midpoints)}

        constraints.update({vertex: rhinocurves[midpoint_map[index]] for index, boundary in enumerate(boundaries) for vertex in boundary})

    if rhinopoints:
        constraints.update(constrained_vertices)

    return constraints
