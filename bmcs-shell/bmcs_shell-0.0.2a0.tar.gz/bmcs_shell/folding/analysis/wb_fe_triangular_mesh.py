import traits.api as tr
import bmcs_utils.api as bu
from bmcs_shell.folding.analysis.fem.fe_triangular_mesh import FETriangularMesh
from bmcs_shell.folding.geometry.wb_shell_geometry import WBShellGeometry
import pygmsh
import numpy as np
import k3d
import gmsh

class WBShellFETriangularMesh(FETriangularMesh):
    """Directly mapped mesh with one-to-one mapping
    """
    name = 'WBShellFETriangularMesh'

    plot_backend = 'k3d'

    geo = bu.Instance(WBShellGeometry)

    I_CDij = tr.DelegatesTo('geo')
    unique_node_map = tr.DelegatesTo('geo')
    n_phi_plus = tr.DelegatesTo('geo')

    direct_mesh = bu.Bool(False, DSC=True)

    subdivision = bu.Float(3, DSC=True)

    # Will be used in the parent class. Should be here to catch GEO dependency
    show_wireframe = bu.Bool(True, GEO=True)

    ipw_view = bu.View(
        *FETriangularMesh.ipw_view.content,
        bu.Item('subdivision'),
        bu.Item('direct_mesh'),
        bu.Item('export_vtk'),
        bu.Item('show_wireframe'),
    )

    mesh = tr.Property(depends_on='state_changed')

    @tr.cached_property
    def _get_mesh(self):

        X_Id = self.geo.X_Ia
        I_Fi = self.geo.I_Fi
        mesh_size = np.linalg.norm(X_Id[1] - X_Id[0]) / self.subdivision

        with pygmsh.geo.Geometry() as geom:
            xpoints = np.array([
                geom.add_point(X_d, mesh_size=mesh_size) for X_d in X_Id
            ])
            for I_i in I_Fi:
                # Create points.

                Facet(geom, xpoints[I_i])
            #                geom.add_polygon(X_id, mesh_size=mesh_size)
            gmsh.model.geo.remove_all_duplicates()
            mesh = geom.generate_mesh()
        return mesh

    X_Id = tr.Property

    def _get_X_Id(self):
        if self.direct_mesh:
            return self.geo.X_Ia
        return np.array(self.mesh.points, dtype=np.float_)

    I_Fi = tr.Property

    def _get_I_Fi(self):
        if self.direct_mesh:
            return self.geo.I_Fi
        return self.mesh.cells[1][1]

    bc_fixed_nodes = tr.Array(np.int_, value=[])
    bc_loaded_nodes = tr.Array(np.int_, value=[])

    export_vtk = bu.Button

    @tr.observe('export_vtk')
    def write(self, event=None):
        self.mesh.write("test_shell_mesh.vtk")

    def setup_plot(self, pb):
        super(WBShellFETriangularMesh, self).setup_plot(pb)

        X_Id = self.X_Id.astype(np.float32)

        fixed_nodes = self.bc_fixed_nodes
        loaded_nodes = self.bc_loaded_nodes

        X_Ma = X_Id[fixed_nodes]
        k3d_fixed_nodes = k3d.points(X_Ma, color=0x22ffff, point_size=100)
        pb.plot_fig += k3d_fixed_nodes
        pb.objects['fixed_nodes'] = k3d_fixed_nodes

        X_Ma = X_Id[loaded_nodes]
        k3d_loaded_nodes = k3d.points(X_Ma, color=0xff22ff, point_size=100)
        pb.plot_fig += k3d_loaded_nodes
        pb.objects['loaded_nodes'] = k3d_loaded_nodes

    def update_plot(self, pb):
        super(WBShellFETriangularMesh, self).update_plot(pb)

        fixed_nodes = self.bc_fixed_nodes
        loaded_nodes = self.bc_loaded_nodes
        X_Id = self.X_Id.astype(np.float32)
        pb.objects['fixed_nodes'].positions = X_Id[fixed_nodes]
        pb.objects['loaded_nodes'].positions = X_Id[loaded_nodes]


class Facet:
    dim = 2

    def __init__(self, host, xpoints):
        # Create lines
        self.curves = [
                          host.add_line(xpoints[k], xpoints[k + 1])
                          for k in range(len(xpoints) - 1)
                      ] + [host.add_line(xpoints[-1], xpoints[0])]

        self.lines = self.curves

        self.curve_loop = host.add_curve_loop(self.curves)
        # self.surface = host.add_plane_surface(ll, holes) if make_surface else None
        self.surface = host.add_plane_surface(self.curve_loop)
        self.dim_tag = self.surface.dim_tag
        self.dim_tags = self.surface.dim_tags
        self._id = self.surface._id

    def __repr__(self):
        return "<pygmsh Polygon object>"