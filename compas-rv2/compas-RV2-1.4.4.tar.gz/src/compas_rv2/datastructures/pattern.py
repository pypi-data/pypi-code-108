from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
from compas.datastructures import Mesh
from compas.datastructures import mesh_smooth_area
from compas.utilities import geometric_key

import compas_rhino

from compas_rv2.singular.algorithms import boundary_triangulation
from compas_rv2.singular.algorithms import SkeletonDecomposition

from .meshmixin import MeshMixin


class Pattern(MeshMixin, Mesh):
    """Customised mesh data structure for RV2.

    Examples
    --------
    A :class:`Pattern` is used to define the geometry and boundary conditions of
    a funicular network in RV2.
    Patterns can be constructed from various inputs.

    >>> pattern = Pattern.from_lines()
    >>> pattern = Pattern.from_mesh()
    >>> pattern = Pattern.from_surface()
    >>> pattern = Pattern.from_skeleton()
    >>> pattern = Pattern.from_features()

    A pattern is essentially a mesh data structure, and therefore supports all operations
    available for meshes. For example,

    """

    def __init__(self, *args, **kwargs):
        super(Pattern, self).__init__(*args, **kwargs)
        self.attributes.update({
            'openings': {}
        })
        self.default_vertex_attributes.update({
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
            'constraints': None,
            'is_fixed': False,
        })
        self.default_edge_attributes.update({
            'q': 1.0,
            'lmin': 1e-6,
            'lmax': 1e6
        })

    @classmethod
    def from_surface_and_features(cls, discretisation, target_edge_length, surf_guid, curve_guids=[], point_guids=[], delaunay=None):
        """Get a pattern object from a NURBS surface with optional point and curve features on the surface.
        The pattern is aligned to the surface boundaries and curve features.
        The pattern contains a pole singularity at the feature points. Pole singularities are a specific type of singularity.

        Parameters
        ----------
        discretisation : float
            The surface boundary and curve feature discretisation length.
            Values between 1% and 5% of the length of the diagonal of the bounding box are recommended.
        target_edge_length : float
            The edge target length for densification.
        surf_guid : str
            A Rhino surface guid.
        curves : list of str, optional
            A list of Rhino curve guids.
        points : list of str, optional
            A list of Rhino point guids.

        Returns
        -------
        Pattern
            A Pattern object.

        References
        ----------
        Based on [1]_ and [2]_.

        .. [1] Oval et al. *Feature-based topology finding of patterns for shell structures*. Automation in Construction, 2019.
               Available at: https://www.researchgate.net/publication/331064073_Feature-based_Topology_Finding_of_Patterns_for_Shell_Structures.
        .. [2] Oval. *Topology finding of patterns for structural design*. PhD thesis, Unversite Paris-Est, 2019.
               Available at: https://www.researchgate.net/publication/340096530_Topology_Finding_of_Patterns_for_Structural_Design.

        """
        from compas_rv2.singular.rhino import RhinoSurface

        compas.PRECISION = '3f'

        compas_rhino.rs.EnableRedraw(False)
        surface = RhinoSurface.from_guid(surf_guid)
        result = surface.discrete_mapping(discretisation, crv_guids=curve_guids, pt_guids=point_guids)
        trimesh = boundary_triangulation(*result, delaunay=delaunay)
        decomposition = SkeletonDecomposition.from_mesh(trimesh)
        coarsemesh = decomposition.decomposition_mesh(result[-1])

        surface.mesh_uv_to_xyz(trimesh)
        surface.mesh_uv_to_xyz(decomposition)
        surface.mesh_uv_to_xyz(coarsemesh)

        gkey_vertex = coarsemesh.gkey_key()
        edge_curve = {}
        curves = []

        for polyline in decomposition.polylines:
            polyline = surface.polyline_uv_to_xyz(polyline)
            a = geometric_key(polyline[0])
            b = geometric_key(polyline[-1])
            u = gkey_vertex[a]
            v = gkey_vertex[b]
            edge_curve[u, v] = polyline

        coarsemesh.collect_strips()
        coarsemesh.set_strips_density_target(target_edge_length)
        coarsemesh.densification(edges_to_curves=edge_curve)
        compas_rhino.delete_objects(curves, purge=True)
        densemesh = coarsemesh.get_quad_mesh()
        compas_rhino.rs.EnableRedraw(True)
        compas_rhino.rs.Redraw()
        return cls.from_vertices_and_faces(*densemesh.to_vertices_and_faces())

    def collapse_small_edges(self, tol=1e-2):
        for key in list(self.edges()):
            if self.has_edge(key):
                u, v = key
                if self.edge_length(u, v) < tol:
                    self.collapse_edge(u, v, t=0.5, allow_boundary=True)

    def smooth(self, fixed, kmax=10):
        mesh_smooth_area(self, fixed=fixed, kmax=kmax)

    def relax(self):
        from compas.numerical import fd_numpy
        key_index = self.key_index()
        xyz = self.vertices_attributes('xyz')
        loads = [[0.0, 0.0, 0.0] for _ in xyz]
        fixed = [key_index[key] for key in self.vertices_where({'is_fixed': True})]
        edges = [(key_index[u], key_index[v]) for u, v in self.edges()]
        q = self.edges_attribute('q')
        xyz, q, f, l, r = fd_numpy(xyz, edges, fixed, q, loads)
        for key in self.vertices():
            index = key_index[key]
            self.vertex_attributes(key, 'xyz', xyz[index])
