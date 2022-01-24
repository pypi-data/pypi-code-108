"""
## Can be probably removed
"""
import bmcs_utils.api as bu
import k3d
from bmcs_shell.folding.geometry.wb_cell_4p import \
    WBElem, axis_angle_to_q, qv_mult
import traits.api as tr
import numpy as np

class WBShell(bu.InteractiveModel):
    name = 'Waterbomb shell'

    wb_cell = tr.Instance(WBElem, ())
    plot_backend = 'k3d'

    n_phi_plus = bu.Float(4, GEO=True)
    n_x_plus = bu.Float(4, GEO=True)
    alpha = bu.Float(1e-5, GEO=True)
    a = bu.Float(1, GEO=True)
    b = bu.Float(1, GEO=True)
    c = bu.Float(1, GEO=True)

    @tr.observe('+GEO', post_init=True)
    def update_wb_cell(self, event):
        self.wb_cell.trait_set(
            alpha=self.alpha,
            a=self.a,
            b=self.b,
            c=self.c
        )

    def get_phi_range(self, delta_phi):
        return np.arange(-(self.n_phi_plus - 1), self.n_phi_plus) * delta_phi

    def get_X_phi_range(self,delta_phi, R_0):
        phi_range = self.get_phi_range((delta_phi))
        return np.array([np.fabs(R_0) * np.sin(phi_range),
                         np.fabs(R_0) * np.cos(phi_range) + R_0]).T

    def get_X_x_range(self,delta_x):
        return np.arange(-(self.n_x_plus - 1), self.n_x_plus) * delta_x

    ipw_view = bu.View(
        bu.Item('alpha', latex=r'\alpha', editor=bu.FloatRangeEditor(
            low=1e-10, high=np.pi / 2, continuous_update=True)),
        bu.Item('a', editor=bu.FloatRangeEditor(low=1e-10, high=10, continuous_update=True)),
        bu.Item('b', editor=bu.FloatRangeEditor(low=1e-10, high=10, continuous_update=True)),
        bu.Item('c', editor=bu.FloatRangeEditor(low=1e-10, high=10, continuous_update=True)),
        bu.Item('n_phi_plus', latex = r'n_\phi'),
        bu.Item('n_x_plus', latex = r'n_x'),
    )

    n_cells = tr.Property
    def _get_n_cells(self):
        delta_x = self.wb_cell.delta_x
        delta_phi = self.wb_cell.delta_phi
        R_0 = self.wb_cell.R_0

        X_x_range = self.get_X_x_range(delta_x)
        X_phi_range = self.get_X_phi_range(delta_phi, R_0)
        n_idx_x = len(X_x_range)
        n_idx_phi = len(X_phi_range)
        idx_x = np.arange(n_idx_x)
        idx_phi = np.arange(n_idx_phi)

        idx_x_ic = idx_x[(n_idx_x) % 2::2]
        idx_x_id = idx_x[(n_idx_x + 1) % 2::2]
        idx_phi_ic = idx_phi[(n_idx_phi) % 2::2]
        idx_phi_id = idx_phi[(n_idx_phi + 1) % 2::2]

        n_ic = len(idx_x_ic) * len(idx_phi_ic)
        n_id = len(idx_x_id) * len(idx_phi_id)

        return n_ic + n_id

    X_Ia = tr.Property(depends_on='+GEO')
    '''Array with nodal coordinates I - node, a - dimension
    '''
    @tr.cached_property
    def _get_X_Ia(self):

        delta_x = self.wb_cell.delta_x
        delta_phi = self.wb_cell.delta_phi
        R_0 = self.wb_cell.R_0

        X_Ia_wb_rot = np.copy(self.wb_cell.X_Ia)
        X_Ia_wb_rot[...,2] -= R_0
        X_cIa = np.array([X_Ia_wb_rot], dtype=np.float_)
        rotation_axes = np.array([[1, 0, 0]], dtype=np.float_)
        rotation_angles = self.get_phi_range(delta_phi)
        q = axis_angle_to_q(rotation_axes, rotation_angles)
        X_dIa = qv_mult(q, X_cIa)
        X_dIa[...,2] += R_0

        #### prototyping

        X_x_range = self.get_X_x_range(delta_x)
        X_phi_range = self.get_X_phi_range(delta_phi, R_0)
        n_idx_x = len(X_x_range)
        n_idx_phi = len(X_phi_range)
        idx_x = np.arange(n_idx_x)
        idx_phi = np.arange(n_idx_phi)

        idx_x_ic = idx_x[(n_idx_x) % 2::2]
        idx_x_id = idx_x[(n_idx_x + 1) % 2::2]
        idx_phi_ic = idx_phi[(n_idx_phi) % 2::2]
        idx_phi_id = idx_phi[(n_idx_phi + 1) % 2::2]

        X_E = X_x_range[idx_x_ic]
        X_F = X_x_range[idx_x_id]

        X_CIa = X_dIa[idx_phi_ic]
        X_DIa = X_dIa[idx_phi_id]

        expand = np.array([1,0,0])
        X_E_a = np.einsum('i,j->ij', X_E, expand)
        X_ECIa = X_CIa[np.newaxis,:,:,:] + X_E_a[:,np.newaxis,np.newaxis,:]
        X_F_a = np.einsum('i,j->ij', X_F, expand)
        X_FDIa = X_DIa[np.newaxis,:,:,:] + X_F_a[:,np.newaxis,np.newaxis,:]

        X_Ia = np.vstack([X_ECIa.flatten().reshape(-1,3), X_FDIa.flatten().reshape(-1,3)])
        return X_Ia

    I_Fi = tr.Property(depends_on='+GEO')
    '''Array with nodal coordinates I - node, a - dimension
    '''
    @tr.cached_property
    def _get_I_Fi(self):
        I_Fi_cell = self.wb_cell.I_Fi
        n_I_cell = self.wb_cell.n_I
        n_cells = self.n_cells
        i_range = np.arange(n_cells) * n_I_cell
        return (I_Fi_cell[np.newaxis,:,:] + i_range[:, np.newaxis, np.newaxis]).reshape(-1,3)

    def update_plot(self, k3d_plot):
        #        X_C_a, X_D_a = self.get_geo()
        wb_cell_mesh_surfaces = k3d.mesh(self.X_Ia.astype(np.float32),
                                         self.I_Fi.astype(np.uint32),
                                         color=0x999999,
                                         side='double')
        k3d_plot += wb_cell_mesh_surfaces

