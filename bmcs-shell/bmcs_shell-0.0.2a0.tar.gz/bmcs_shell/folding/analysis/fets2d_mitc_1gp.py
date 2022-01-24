import traits.api as tr
from ibvpy.fets import FETSEval
from ibvpy.mathkit.tensor import DELTA23_ab
import numpy as np


class FETS2DMITC(FETSEval):
    r'''MITC3 shell finite element:
        See https://www.sesamx.io/blog/standard_linear_triangular_shell_element/
        See http://dx.doi.org/10.1016/j.compstruc.2014.02.005
    '''

    vtk_r = tr.Array(np.float_, value=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    vtk_cells = [[0, 1, 2]]
    vtk_cell_types = 'Triangle'
    vtk_cell = [0, 1, 2]
    vtk_cell_type = 'Triangle'

    vtk_expand_operator = tr.Array(np.float_, value=DELTA23_ab)

    # =========================================================================
    # Surface integrals using numerical integration
    # =========================================================================
    # i is point indices, p is point coords in natural coords (zeta_1, zeta_2, zeta_3)
    eta_ip = tr.Array('float_')
    r'''Integration points within a triangle.
    '''

    def _eta_ip_default(self):
        # We applay the 7-point Gauss integration to integrate exactly on the plane defined by rr and ss
        # [r, s, t] at each Gauss point (r, s, t) are natural coords in the shell element r,s in plane
        # and t along thickness
        # 2 Gauss points along thickness t
        # 7 Gauss points on the plane of the element
        return np.array([[1. / 3., 1. / 3., 1. / 3.]], dtype='f')

    w_m = tr.Array('float_')
    r'''Weight factors for numerical integration.
    '''

    def _w_m_default(self):
        return np.array([1. / 2.], dtype='f')

    # TODO, different node thickness in each node according to the original
    #  implementation can be easily integrated, but here the same thickness
    #  is used for simplicity.
    a = tr.Float(1.0,
                 label='thickness')

    n_m = tr.Int(1)
    r'''Number of integration points.
    '''

    @tr.cached_property
    def _get_n_m(self):
        return len(self.w_m)

    n_nodal_dofs = tr.Int(5)

    N_im = tr.Property(depends_on='eta_ip')
    r'''Shape function values in integration points.
    '''

    @tr.cached_property
    def _get_N_im(self):
        # Shouldn't be mi instead of im?
        eta = self.eta_ip
        return np.array([1 - eta[:, 0] - eta[:, 1], eta[:, 0], eta[:, 1]],
                        dtype='f')

    dh_imr = tr.Property(depends_on='eta_ip')
    r'''Derivatives of the shape functions in the integration points.
    '''

    @tr.cached_property
    def _get_dh_imr(self):
        # Same for all Gauss points
        dh_ri = np.array([[-1, 1, 0],       # dh1/d_r, dh2/d_r, dh3/d_r
                           [-1, 0, 1],      # dh1/d_s, dh2/d_s, dh3/d_s
                           [0, 0, 0]],      # dh1/d_t, dh2/d_t, dh3/d_t
                          dtype=np.float_)
        dh_mri = np.tile(dh_ri, (self.n_m, 1, 1))

        return np.einsum('mri->imr', dh_mri)

    dht_imr = tr.Property(depends_on='eta_ip')
    r'''Derivatives of the (shape functions * t) in the integration points.
    '''

    @tr.cached_property
    def _get_dht_imr(self):
        # m: gauss points, r: r, s, t, and i: h1, h2, h3
        eta_ip = self.eta_ip
        dh_mri = np.array([[[-t, t, 0],         # (t*dh1)/d_r, (t*dh2)/d_r, (t*dh3)/d_r
                            [-t, 0, t],         # (t*dh1)/d_s, (t*dh2)/d_s, (t*dh3)/d_s
                            [1 - r - s, r, s]]  # (t*dh1)/d_t, (t*dh2)/d_t, (t*dh3)/d_t
                           for r, s, t in zip(eta_ip[:, 0], eta_ip[:, 1], eta_ip[:, 2])],
                          dtype=np.float_)
        return np.einsum('mri->imr', dh_mri)

    dh_inr = tr.Property(depends_on='eta_ip')
    r'''Derivatives of the shape functions in the integration points.
    '''

    @tr.cached_property
    def _get_dh_inr(self):
        return self.dh_imr

    def get_B(self):
        pass

    vtk_expand_operator = tr.Array(value=[1, 1, 0])
    vtk_node_cell_data = tr.Array
    vtk_ip_cell_data = tr.Array
