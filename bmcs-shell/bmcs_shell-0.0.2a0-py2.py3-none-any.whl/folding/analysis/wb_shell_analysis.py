import k3d
import numpy as np

from bmcs_shell.folding.analysis.abaqus.abaqus_link_simple import AbaqusLink
from bmcs_shell.folding.analysis.fem.tri_xdomain_fe_mitc import TriXDomainMITC
from bmcs_shell.folding.analysis.fem.vmats2D_elastic import MATS2DElastic
from ibvpy.sim.tstep_bc import TStepBC
import bmcs_utils.api as bu
import traits.api as tr
from ibvpy.bcond import BCDof
from bmcs_shell.folding.analysis.fem.tri_xdomain_fe import TriXDomainFE
from bmcs_shell.folding.analysis.fem.bcs import BoundaryConditions
from bmcs_shell.folding.analysis.fem.vmats_shell_elastic import MATSShellElastic
from bmcs_shell.folding.analysis.fets2d_mitc import FETS2DMITC
from bmcs_shell.folding.geometry.wb_shell_geometry import WBShellGeometry
from bmcs_shell.folding.analysis.wb_fe_triangular_mesh import WBShellFETriangularMesh

itags_str = '+GEO,+MAT,+BC'


class WBShellAnalysis(TStepBC, bu.InteractiveModel):
    name = 'WBShellAnalysis'
    plot_backend = 'k3d'
    id = bu.Str
    """ if you saved boundary conditions for your current analysis, this id will make sure these bcs
     are loaded automatically next time you create an instance with the same id """

    h = bu.Float(10, GEO=True)
    show_wireframe = bu.Bool(True, GEO=True)

    ipw_view = bu.View(
        bu.Item('h',
                editor=bu.FloatRangeEditor(low=1, high=100, n_steps=100),
                continuous_update=False),
        bu.Item('show_wireframe'),
        time_editor=bu.ProgressEditor(run_method='run',
                                      reset_method='reset',
                                      interrupt_var='interrupt',
                                      time_var='t',
                                      time_max='t_max'),
    )

    n_phi_plus = tr.Property()

    def _get_n_phi_plus(self):
        return self.xdomain.mesh.n_phi_plus

    tree = ['geo', 'bcs', 'tmodel', 'xdomain']

    geo = bu.Instance(WBShellGeometry, ())

    tmodel = bu.Instance(MATS2DElastic, ())
    # tmodel = bu.Instance(MATSShellElastic, ())

    bcs = bu.Instance(BoundaryConditions)
    def _bcs_default(self):
        return BoundaryConditions(geo=self.geo, n_nodal_dofs=self.xdomain.fets.n_nodal_dofs, id=self.id)

    xdomain = tr.Property(tr.Instance(TriXDomainFE),
                          depends_on="state_changed")
    '''Discretization object.'''

    @tr.cached_property
    def _get_xdomain(self):
        # prepare the mesh generator
        # mesh = WBShellFETriangularMesh(geo=self.geo, direct_mesh=False, subdivision=2)
        mesh = WBShellFETriangularMesh(geo=self.geo, direct_mesh=True)
        # construct the domain with the kinematic strain mapper and stress integrator
        return TriXDomainFE(
            mesh=mesh,
            integ_factor=self.h,
        )

        # mesh = WBShellFETriangularMesh(geo=self.geo, direct_mesh=True)
        # mesh.fets = FETS2DMITC(a= self.h)
        # return TriXDomainMITC(
        #     mesh=mesh
        # )

    domains = tr.Property(depends_on="state_changed")

    @tr.cached_property
    def _get_domains(self):
        return [(self.xdomain, self.tmodel)]

    def reset(self):
        self.sim.reset()

    t = tr.Property()

    def _get_t(self):
        return self.sim.t

    def _set_t(self, value):
        self.sim.t = value

    t_max = tr.Property()

    def _get_t_max(self):
        return self.sim.t_max

    def _set_t_max(self, value):
        self.sim.t_max = value

    interrupt = tr.Property()

    def _get_interrupt(self):
        return self.sim.interrupt

    def _set_interrupt(self, value):
        self.sim.interrupt = value

    bc = tr.Property(depends_on="state_changed")
    # @tr.cached_property
    def _get_bc(self):
        bc_fixed, _, _ = self.bcs.bc_fixed
        bc_loaded, _, _ = self.bcs.bc_loaded
        return bc_fixed + bc_loaded

    def run(self):
        s = self.sim
        s.tloop.k_max = 10
        s.tline.step = 1
        s.tloop.verbose = False
        s.run()

    def get_max_vals(self):
        self.run()
        U_1 = self.hist.U_t[-1]
        U_max = np.max(np.fabs(U_1))
        return U_max

    def export_abaqus(self):
        al = AbaqusLink(shell_analysis=self)
        al.model_name = 'test_name'
        al.build_inp()

    def setup_plot(self, pb):
        print('analysis: setup_plot')
        X_Id = self.xdomain.mesh.X_Id
        if len(self.hist.U_t) == 0:
            U_1 = np.zeros_like(X_Id)
            print('analysis: U_I', )
        else:
            U_1 = self.hist.U_t[-1]
            U_1 = U_1.reshape(-1, self.xdomain.fets.n_nodal_dofs)[:, :3]

        X1_Id = X_Id + U_1
        X1_Id = X1_Id.astype(np.float32)

        I_Ei = self.xdomain.I_Ei.astype(np.uint32)

        # Original state mesh
        wb_mesh_0 = k3d.mesh(self.xdomain.X_Id.astype(np.float32),
                             I_Ei,
                             color=0x999999, opacity=0.5,
                             side='double')
        pb.plot_fig += wb_mesh_0
        pb.objects['wb_mesh_0'] = wb_mesh_0

        # Deformed state mesh
        wb_mesh_1 = k3d.mesh(X1_Id,
                             I_Ei,
                             color_map=k3d.colormaps.basic_color_maps.Jet,
                             attribute=U_1[:, 2],
                             color_range=[np.min(U_1), np.max(U_1)],
                             side='double')
        pb.plot_fig += wb_mesh_1
        pb.objects['wb_mesh_1'] = wb_mesh_1

        if self.show_wireframe:
            k3d_mesh_wireframe = k3d.mesh(X1_Id,
                                          I_Ei,
                                          color=0x000000,
                                          wireframe=True)
            pb.plot_fig += k3d_mesh_wireframe
            pb.objects['mesh_wireframe'] = k3d_mesh_wireframe

    def update_plot(self, pb):
        X_Id = self.xdomain.mesh.X_Id
        print('analysis: update_plot')
        if len(self.hist.U_t) == 0:
            U_1 = np.zeros_like(X_Id)
            print('analysis: U_I', )
        else:
            U_1 = self.hist.U_t[-1]
            U_1 = U_1.reshape(-1, self.xdomain.fets.n_nodal_dofs)[:, :3]

        X1_Id = X_Id + U_1
        X1_Id = X1_Id.astype(np.float32)

        I_Ei = self.xdomain.I_Ei.astype(np.uint32)

        mesh = pb.objects['wb_mesh_1']
        mesh.vertices = X1_Id
        mesh.indices = I_Ei
        mesh.attribute = U_1[:, 2]
        mesh.color_range = [np.min(U_1), np.max(U_1)]
        if self.show_wireframe:
            wireframe = pb.objects['mesh_wireframe']
            wireframe.vertices = X1_Id
            wireframe.indices = I_Ei

    def get_Pw(self):
        import numpy as np
        F_to = self.hist.F_t
        U_to = self.hist.U_t
        _, _, loaded_dofs = self.bcs.bc_loaded
        F_loaded = np.sum(F_to[:, loaded_dofs], axis=-1)
        U_loaded = np.average(U_to[:, loaded_dofs], axis=-1)
        return U_loaded, F_loaded
