
import traits.api as tr
from ibvpy.fets import FETSEval
from ibvpy.mathkit.tensor import DELTA23_ab
import numpy as np


class FETS2D3U1M(FETSEval):
    r'''Triangular, three-node element.
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
        # here, just one integration point in the middle of the triangle (zeta_1 = 1/3, zeta_2 = 1/3, zeta_3 = 1/3)
        return np.array([[1. / 3., 1. / 3., 1. / 3.]], dtype='f')

    w_m = tr.Array('float_')
    r'''Weight factors for numerical integration.
    '''

    def _w_m_default(self):
        return np.array([1. / 2.], dtype='f')

    n_m = tr.Int(1)
    r'''Number of integration points.
    '''
    @tr.cached_property
    def _get_w_m(self):
        return len(self.w_m)

    n_nodal_dofs = tr.Int(3)

    N_im = tr.Property(depends_on='eta_ip')
    r'''Shape function values in integration points.
    '''
    @tr.cached_property
    def _get_N_im(self):
        eta = self.eta_ip
        return np.array([eta[:, 0], eta[:, 1], 1 - eta[:, 0] - eta[:, 1]],
                        dtype='f')

    dN_imr = tr.Property(depends_on='eta_ip')
    r'''Derivatives of the shape functions in the integration points.
    '''
    @tr.cached_property
    def _get_dN_imr(self):
        dN_mri = np.array([[[1, 0, -1],         # dN1/d_zeta1, dN2/d_zeta1, dN3/d_zeta1
                          [0, 1, -1]],          # dN1/d_zeta2, dN2/d_zeta2, dN3/d_zeta2
                          ], dtype=np.float_)
        return np.einsum('mri->imr', dN_mri)

    dN_inr = tr.Property(depends_on='eta_ip')
    r'''Derivatives of the shape functions in the integration points.
    '''
    @tr.cached_property
    def _get_dN_inr(self):
        return self.dN_imr

    vtk_expand_operator = tr.Array(value=[1,1,0])
    vtk_node_cell_data = tr.Array
    vtk_ip_cell_data = tr.Array
