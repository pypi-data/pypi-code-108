# Indices reference:
# ------------------
# m: num of Gauss points
# r: num of curvilinear (natural) coordinates (r, s, t)
# i: num of shape functions max = 3, (h1, h2, h3)
# i: num of nodes in each element max = 3, (0, 1, 2)
# F: global num of elements?
# E: global num of elements?
# a: coordinates (x, y, z)
# b: coordinates (x, y, z)
# c: coordinates (x, y, z)
# d: coordinates (x, y, z)

import traits.api as tr
from ibvpy.mathkit.tensor import DELTA23_ab
import numpy as np

from bmcs_shell.folding.analysis.fets2d_mitc import FETS2DMITC
from bmcs_shell.folding.utils.vector_acos import \
    get_theta, get_theta_du
import k3d
from ibvpy.mathkit.linalg.sys_mtx_assembly import SysMtxArray
import bmcs_utils.api as bu

INPUT = '+cp_input'


# Kronecker delta
DELTA = np.zeros((3, 3,), dtype='f')
DELTA[(0, 1, 2), (0, 1, 2)] = 1

# Levi Civita symbol
EPS = np.zeros((3, 3, 3), dtype='f')
EPS[(0, 1, 2), (1, 2, 0), (2, 0, 1)] = 1
EPS[(2, 1, 0), (1, 0, 2), (0, 2, 1)] = -1

from bmcs_shell.folding.analysis.fem.fe_triangular_mesh import FETriangularMesh
from bmcs_shell.folding.analysis.fem.xdomain_fe_grid import XDomainFE

class TriXDomainMITC(XDomainFE):
    name = 'TriXDomainFE'
    '''
    Finite element discretization with dofs and mappings derived from the FE definition
    '''

    mesh = tr.Instance(FETriangularMesh)
    def _mesh_default(self):
        return FETriangularMesh(fets=FETS2DMITC())

    fets = tr.DelegatesTo('mesh')

    tree = ['mesh']

    change = tr.Event(GEO=True)

    plot_backend = 'k3d'

    n_dofs = tr.Property

    def _get_n_dofs(self):
        return len(self.mesh.X_Id) * self.mesh.n_nodal_dofs

    eta_w = tr.Property
    r'''Weight factors for numerical integration.
    '''

    def _get_eta_w(self):
        return self.fets.w_m

    Na_deta = tr.Property()
    r'''Derivatives of the shape functions in the integration points.
    '''
    @tr.cached_property
    def _get_Na_deta(self):
        return np.einsum('imr->mri', self.fets.dh_imr)

    x_0 = tr.Property()
    r'''Derivatives of the shape functions in the integration points.
    '''
    @tr.cached_property
    def _get_x_0(self):
        return self.mesh.X_Id

    x = tr.Property()
    r'''Derivatives of the shape functions in the integration points.
    '''
    @tr.cached_property
    def _get_x(self):
        return self.x_0

    F = tr.Property()
    r'''Derivatives of the shape functions in the integration points.
    '''
    @tr.cached_property
    def _get_F(self):
        return self.mesh.I_Fi

    T_Fab = tr.Property(depends_on='+GEO')
    @tr.cached_property
    def _get_T_Fab(self):
        return self.F_L_bases[:, 0, :]

    I_Ei = tr.Property
    def _get_I_Ei(self):
        return self.F_N

    x_Eia = tr.Property(depends_on='+GEO')
    @tr.cached_property
    def _get_x_Eia(self):
        X_Eia = self.X_Id[self.I_Ei, :]
        X_E0a = X_Eia[:, 0, :]
        X_Eia -= X_E0a[:, np.newaxis, :]
        X_Eic = np.einsum('Eac,Eic->Eia', self.T_Fab, X_Eia)
        return X_Eic[...,:-1]

    def U2u(self, U_Eia):
        u0_Eia = U_Eia[...,:-1]
        return u0_Eia

    def xU2u(self, U_Eia):
        u1_Eia = np.einsum('Eab,Eib->Eia', self.T_Fab, U_Eia)
        u2_Eie =  np.einsum('ea,Eia->Eie', DELTA23_ab, u1_Eia)
        return u2_Eie

    def f2F(self, f_Eid):
        F0_Eia = np.concatenate( [f_Eid, np.zeros_like(f_Eid[...,:1])], axis=-1)
        return F0_Eia

    def xf2F(self, f_Eid):
        F1_Eia = np.einsum('da,Eid->Eia', DELTA23_ab, f_Eid)
        F2_Eia = np.einsum('Eab,Eia->Eib', self.T_Fab, F1_Eia)
        return F2_Eia

    def k2K(self, K_Eiejf):
        K0_Eicjf = np.concatenate( [K_Eiejf, np.zeros_like(K_Eiejf[:,:,:1,:,:])], axis=2)
        K0_Eicjd = np.concatenate( [K0_Eicjf, np.zeros_like(K0_Eicjf[:,:,:,:,:1])], axis=4)
        return K0_Eicjd

    def xk2K(self, K_Eiejf):
        K1_Eiejf = np.einsum('ea,fb,Eiejf->Eiajb', DELTA23_ab, DELTA23_ab, K_Eiejf) # correct
        T_Eeafb = np.einsum('Eea,Efb->Eeafb', self.T_Fab, self.T_Fab)
        #K_Eab = np.einsum('Eeafb,ef->Eab', T_Eeafb, k_ef)
        K2_Eiajb = np.einsum('Eeafb,Eiejf->Eiajb', T_Eeafb, K1_Eiejf)
        #K2_Eicjd = np.einsum('Eca,Ebd,Eiajb->Eicjd', self.T_Fab, self.T_Fab, K1_Eicjd)
        #K2_Eicjd = np.einsum('Eac,Edb,Eiajb->Eicjd', self.T_Fab, self.T_Fab, K1_Eicjd)
        return K2_Eiajb

    I_CDij = tr.Property
    def _get_I_CDij(self):
        return self.mesh.I_CDij

    bc_J_F_xyz= tr.Property(depends_on='state_changed')
    @tr.cached_property
    def _get_bc_J_F_xyz(self):
        ix2 = int((self.mesh.n_phi_plus) / 2)
        F_I = self.I_CDij[ix2, :, 0, :].flatten()
        _, idx_remap = self.mesh.unique_node_map
        return idx_remap[F_I]

    bc_J_xyz = tr.Property(depends_on='state_changed')
    @tr.cached_property
    def _get_bc_J_xyz(self):
        I_M = self.I_CDij[(0, -1), :, (0, -1), :].flatten()
        _, idx_remap = self.mesh.unique_node_map
        J_M = idx_remap[I_M]
        return J_M

    bc_J_x = tr.Property(depends_on='state_changed')
    @tr.cached_property
    def _get_bc_J_x(self):
        I_M = self.I_CDij[:, (0, -1), :, (0, -1)].flatten()
        _, idx_remap = self.mesh.unique_node_map
        J_M = idx_remap[I_M]
        return J_M

    def setup_plot(self, pb):
        X_Ia = self.mesh.X_Ia.astype(np.float32)
        I_Fi = self.mesh.I_Fi.astype(np.uint32)

        X_Ma = X_Ia[self.bc_J_xyz]
        self.k3d_fixed_xyz = k3d.points(X_Ma)
        pb.plot_fig += self.k3d_fixed_xyz

        X_Ma = X_Ia[self.bc_J_x]
        self.k3d_fixed_x = k3d.points(X_Ma, color=0x22ffff)
        pb.plot_fig += self.k3d_fixed_x

        X_Ma = X_Ia[self.bc_J_F_xyz]
        self.k3d_load_z = k3d.points(X_Ma, color=0xff22ff)
        pb.plot_fig += self.k3d_load_z

        self.k3d_mesh = k3d.mesh(X_Ia,
                                 I_Fi,
                                 color=0x999999,
                                 side='double')
        pb.plot_fig += self.k3d_mesh

    def update_plot(self, pb):
        X_Ia = self.mesh.X_Ia.astype(np.float32)
        I_Fi = self.mesh.I_Fi.astype(np.uint32)

        self.k3d_fixed_xyz.positions = X_Ia[self.bc_J_xyz]
        self.k3d_fixed_x.positions = X_Ia[self.bc_J_x]
        self.k3d_load_z.positions = X_Ia[self.bc_J_F_xyz]

        mesh = self.k3d_mesh
        mesh.vertices = X_Ia
        mesh.indices = I_Fi

    def _get_du_dr_Fmra(self, U_o):
        dh_imr = self.fets.dh_imr
        dht_imr = self.fets.dht_imr
        _, v1_Fid, v2_Fid = self.v_vectors
        a = self.fets.a

        # Calculating du_dr
        U_o = np.arange(3 * 5) # TODO U_o comes from function arguments, this is just for testing
        nodes_num = self.mesh.X_Id.shape[0]
        U_Ie = np.reshape(U_o, (nodes_num, self.fets.n_nodal_dofs))
        U_Fie = U_Ie[self.mesh.I_Fi]
        disp_U_Fia = U_Fie[..., :3]
        rot_U_Fib = U_Fie[..., 3:]
        du_dr1_Fmria = np.einsum('Fia, imr ->Fmria', disp_U_Fia, dh_imr)
        du_dr1_Fmra = np.sum(du_dr1_Fmria, axis=3)

        alpha_idx = 0
        beta_idx = 1
        alpha_Fi1 = rot_U_Fib[..., alpha_idx, np.newaxis]
        beta_Fi1 = rot_U_Fib[..., beta_idx, np.newaxis]
        v2_alpha_Fid = v2_Fid * alpha_Fi1
        v1_beta_Fid = v1_Fid * beta_Fi1
        v1_v2_dif_Fid = v1_beta_Fid - v2_alpha_Fid
        du_dr2_Fmria = np.einsum('Fia, imr ->Fmria', 0.5 * a * v1_v2_dif_Fid, dht_imr)
        du_dr2_Fmra = np.sum(du_dr2_Fmria, axis=3)
        du_dr_Fmra = du_dr1_Fmra + du_dr2_Fmra
        return du_dr_Fmra

    v_vectors = tr.Property(depends_on='+GEO')
    @tr.cached_property
    def _get_v_vectors(self):
        # See P. 472 FEM by Zienkiewicz (ISBN: 1856176339)
        # Calculating v_n (director vector)
        n_Fd = self.norm_F_normals
        el_nodes_num = 3
        Vn_Fid = np.tile(n_Fd, (1, 1, el_nodes_num)).reshape(n_Fd.shape[0], n_Fd.shape[1], el_nodes_num)

        # Calculating v1 and v2 (vectors perpendicular to director vector)
        min_Fi1 = Vn_Fid.argmin(axis=2)
        min_Fi1 = min_Fi1[..., np.newaxis]
        tmp_Fid = np.zeros_like(Vn_Fid, dtype=np.int_)
        tmp_Fid[..., :] = np.arange(3)
        min_mask_Fid = tmp_Fid == min_Fi1
        e_x_min_Fid = min_mask_Fid * 1
        V1_Fid = np.cross(e_x_min_Fid, Vn_Fid)
        V2_Fid = np.cross(Vn_Fid, V1_Fid)
        v1_Fid = self._normalize(V1_Fid)
        v2_Fid = self._normalize(V2_Fid)

        return Vn_Fid, v1_Fid, v2_Fid

    def _normalize(self, V_Fid):
        mag_n = np.sqrt(np.einsum('...i,...i', V_Fid, V_Fid))
        v_Fid = V_Fid / mag_n[:, np.newaxis]
        return v_Fid

    dx_dr_Fmrd = tr.Property(depends_on='+GEO')
    @tr.cached_property
    def _get_dx_dr_Fmrd(self):
        Vn_Fid, _, _ = self.v_vectors

        dh_imr = self.fets.dh_imr
        dht_imr = self.fets.dht_imr

        X_Fid = self.X_Id[self.mesh.I_Fi]
        a = self.fets.a  # thickness (TODO, make it available as input)
        dx_dr1_Fmrid = np.einsum('Fid, imr -> Fmrid', X_Fid, dh_imr)
        dx_dr2_Fmrid = np.einsum('Fid, imr -> Fmrid', 0.5 * a * Vn_Fid, dht_imr)

        dx_dr1_Fmrd = np.sum(dx_dr1_Fmrid, axis=3)
        dx_dr2_Fmrd = np.sum(dx_dr2_Fmrid, axis=3)
        dx_dr_Fmrd = dx_dr1_Fmrd + dx_dr2_Fmrd
        return dx_dr_Fmrd

    dN_dr_Emrco = tr.Property(depends_on='+GEO')
    @tr.cached_property
    def _get_dN_dr_Emrco(self):
        # thickness
        a = self.fets.a
        _, v1_Fid, v2_Fid = self.v_vectors
        dh_imr = self.fets.dh_imr
        dht_imr = self.fets.dht_imr

        element_dofs = 3 * self.fets.n_nodal_dofs
        dN_dr_Emrco = np.zeros((*self.dx_dr_Fmrd.shape, element_dofs))
        # Filling first 3x3 elements from N matrices
        dofs = 5
        # Looping r, s, t
        for i in range(3):
            # Looping h1, h2, h3
            for j in range(3):
                dN_dr_Emrco[..., i, :, 0 + j * dofs:3 + j * dofs] = np.identity(3) * dh_imr[
                    j, 0, i]  # dh1/dr (which is the same for all gaus points)
                # Example: dh_imr[2, 1, 0] is dh3/dr for the second Gauss point
        N4_Fmrai = np.einsum('Fia, imr ->Fmrai', -0.5 * a * v2_Fid, dht_imr)
        N5_Fmrai = np.einsum('Fia, imr ->Fmrai', +0.5 * a * v1_Fid, dht_imr)
        dN_dr_Emrco[..., :, [3, 8, 13]] = N4_Fmrai
        dN_dr_Emrco[..., :, [4, 9, 14]] = N5_Fmrai
        return dN_dr_Emrco

    B_Emiabo = tr.Property(depends_on='+GEO')
    @tr.cached_property
    def _get_B_Emiabo(self):
        delta35_co = np.zeros((3, 5), dtype='f')
        delta35_co[(0, 1, 2), (0, 1, 2)] = 1
        delta25_vo = np.zeros((2, 5), dtype='f')
        delta25_vo[(0, 1), (3, 4)] = 1

        _, v1_Fid, v2_Fid = self.v_vectors
        V_Ficv = np.zeros((*v2_Fid.shape, 2), dtype='f')
        V_Ficv[..., 0] = v1_Fid
        V_Ficv[..., 1] = v2_Fid

        # Thickness a
        a = self.fets.a
        dN_imr = self.fets.dh_imr
        dNt_imr = self.fets.dht_imr

        delta = np.identity(3)
        Diff1_abcd = 0.5 * (
                np.einsum('ac,bd->abcd', delta, delta) +
                np.einsum('ad,bc->abcd', delta, delta)
        )

        J_Fmrd = self.dx_dr_Fmrd

        inv_J_Fmrd = np.linalg.inv(J_Fmrd)
        det_J_Fm = np.linalg.det(J_Fmrd)
        B1_Emiabo = np.einsum('abcd, imr, co, Emrd -> Emiabo', Diff1_abcd, dN_imr, delta35_co, inv_J_Fmrd)
        B2_Emiabo = np.einsum('abcd, imr, Ficv, vo, Emrd -> Emiabo', Diff1_abcd, dNt_imr, 0.5 * a * V_Ficv, delta25_vo,
                              inv_J_Fmrd)
        B_Emiabo = B1_Emiabo + B2_Emiabo

        # B_Emiabo = np.flip(B_Emiabo, 2)

        return B_Emiabo, det_J_Fm

    def _get_B_Empf(self):
        B_Emiabo, _ = self.B_Emiabo
        # Mapping ab to p (3x3 -> 5)
        B_Emipo = B_Emiabo[:, :, :, (0, 1, 0, 1, 2), (0, 1, 1, 2, 0), :]

        E, m, i, p, o = B_Emipo.shape
        B_Empio = np.einsum('Emipo->Empio', B_Emipo)
        B_Empf = B_Empio.reshape((E, m, p, 3 * o))
        # p: index with max value 5
        # f: index with max value 15
        return B_Empf

    def map_U_to_field(self, U_o):
        # print('map_U_to_field')
        # # For testing with one element:
        # U_io = np.array([[1, 0, 0, 0, 0],
        #                  [0, 0, 0.5, 0, 0],
        #                  [0, 1, 0, 0, 0]], dtype=np.float_)
        print('U_o:', U_o)

        # TODO: check if the transformation caused by following line is needed
        U_Eio = U_o[self.o_Eia]
        print('U_Eio,', U_Eio)
        # U_Eio = U_o.reshape((-1, self.fets.n_nodal_dofs))[self.mesh.I_Fi]
        # print('U_Eio,', U_Eio)

        B_Emiabo, _ = self.B_Emiabo

        eps_Emab = np.einsum('Emiabo, Eio -> Emab', B_Emiabo, U_Eio)

        eps_Emp = eps_Emab[:, :, (0, 1, 0, 1, 0), (0, 1, 1, 2, 2)]
        return eps_Emp

    # o_Eia = tr.Property(depends_on='MESH,GEO,CS,FE')
    #
    # @tr.cached_property
    # def _get_o_Eia(self):
    #     I_Fi = self.mesh.I_Fi
    #     return self.o_Ia[I_Fi]

    def map_field_to_F(self, sig_Ems):
        # print('map_field_to_F')
        # print('sig_Es', sig_Ems)

        _, det_J_Fm = self.B_Emiabo

        B_Empf = self._get_B_Empf()
        f_Emf = self.integ_factor * np.einsum('m, Emsf, Ems, Em -> Emf', self.fets.w_m, B_Empf, sig_Ems, det_J_Fm)
        f_Ef = np.sum(f_Emf, axis=1)

        o_Ei = self.o_Eia.reshape(-1, 3 * 5)

        return o_Ei.flatten(), f_Ef.flatten()

    def map_field_to_K(self, D_Est):
        # print('map_field_to_K')
        w_m = self.fets.w_m  # Gauss points weights
        B_Emiabo, det_J_Fm = self.B_Emiabo

        B_Empf = self._get_B_Empf()
        k2_Emop = self.integ_factor * np.einsum('m, Empf, Ept, Emtq, Em -> Emfq', w_m, B_Empf, D_Est, B_Empf,
                                                   det_J_Fm)
        k2_Eop = np.sum(k2_Emop, axis=1)

        o_Ei = self.o_Eia.reshape(-1, 3 * 5)
        return SysMtxArray(mtx_arr=k2_Eop, dof_map_arr=o_Ei)

    # =========================================================================
    # Property operators for initial configuration
    # =========================================================================
    F0_normals = tr.Property(tr.Array, depends_on='X, L, F')
    r'''Normal facet vectors.
    '''
    @tr.cached_property
    def _get_F0_normals(self):
        x_F = self.x_0[self.F]
        N_deta_ip = self.Na_deta
        r_deta = np.einsum('ajK,IKi->Iaij', N_deta_ip, x_F)
        Fa_normals = np.einsum('Iai,Iaj,ijk->Iak',
                               r_deta[..., 0], r_deta[..., 1], EPS)
        return np.sum(Fa_normals, axis=1)

    sign_normals = tr.Property(tr.Array, depends_on='X,L,F')
    r'''Orientation of the normal in the initial state.
    This array is used to switch the normal vectors of the faces
    to be oriented in the positive sense of the z-axis.
    '''
    @tr.cached_property
    def _get_sign_normals(self):
        return np.sign(self.F0_normals[:, 2])

    F_N = tr.Property(tr.Array, depends_on='X,L,F')
    r'''Counter-clockwise enumeration.
    '''
    @tr.cached_property
    def _get_F_N(self):
        turn_facets = np.where(self.sign_normals < 0)
        F_N = np.copy(self.F)
        F_N[turn_facets, :] = self.F[turn_facets, ::-1]
        return F_N

    F_normals = tr.Property(tr.Array, depends_on=INPUT)
    r'''Get the normals of the facets.
    '''
    @tr.cached_property
    def _get_F_normals(self):
        n = self.Fa_normals
        return np.sum(n, axis=1)

    F_normals_0 = tr.Property(tr.Array, depends_on=INPUT)
    r'''Get the normals of the facets.
    '''
    @tr.cached_property
    def _get_F_normals_0(self):
        n = self.Fa_normals_0
        return np.sum(n, axis=1)

    norm_F_normals = tr.Property(tr.Array, depends_on=INPUT)
    r'''Get the normed normals of the facets.
    '''
    @tr.cached_property
    def _get_norm_F_normals(self):
        n = self.F_normals
        mag_n = np.sqrt(np.einsum('...i,...i', n, n))
        return n / mag_n[:, np.newaxis]

    norm_F_normals_0 = tr.Property(tr.Array, depends_on=INPUT)
    r'''Get the normed normals of the facets.
    '''
    @tr.cached_property
    def _get_norm_F_normals_0(self):
        n = self.F_normals_0
        mag_n = np.sqrt(np.einsum('...i,...i', n, n))
        return n / mag_n[:, np.newaxis]

    F_normals_du = tr.Property(tr.Array, depends_on=INPUT)
    r'''Get the normals of the facets.
    '''
    @tr.cached_property
    def _get_F_normals_du(self):
        n_du = self.Fa_normals_du
        return np.sum(n_du, axis=1)

    F_area = tr.Property(tr.Array, depends_on=INPUT)
    r'''Get the surface area of the facets.
    '''
    @tr.cached_property
    def _get_F_area(self):
        a = self.Fa_area
        A = np.einsum('a,Ia->I', self.eta_w, a)
        return A

    # =========================================================================
    # Potential energy
    # =========================================================================
    F_V = tr.Property(tr.Array, depends_on=INPUT)
    r'''Get the total potential energy of gravity for each facet
    '''
    @tr.cached_property
    def _get_F_V(self):
        eta_w = self.eta_w
        a = self.Fa_area
        ra = self.Fa_r
        F_V = np.einsum('a,Ia,Ia->I', eta_w, ra[..., 2], a)
        return F_V

    F_V_du = tr.Property(tr.Array, depends_on=INPUT)
    r'''Get the derivative of total potential energy of gravity for each facet
    with respect to each node and displacement component [FIi]
    '''
    @tr.cached_property
    def _get_F_V_du(self):
        r = self.Fa_r
        a = self.Fa_area
        a_dx = self.Fa_area_du
        r3_a_dx = np.einsum('Ia,IaJj->IaJj', r[..., 2], a_dx)
        N_eta_ip = self.Na
        r3_dx = np.einsum('aK,KJ,j->aJj', N_eta_ip, DELTA, DELTA[2, :])
        a_r3_dx = np.einsum('Ia,aJj->IaJj', a, r3_dx)
        F_V_du = np.einsum('a,IaJj->IJj', self.eta_w, (a_r3_dx + r3_a_dx))
        return F_V_du

    # =========================================================================
    # Line vectors
    # =========================================================================

    F_L_vectors_0 = tr.Property(tr.Array, depends_on=INPUT)
    r'''Get the cycled line vectors around the facet
    The cycle is closed - the first and last vector are identical.

    .. math::
        v_{pld} \;\mathrm{where} \; p\in\mathcal{F}, l\in (0,1,2), d\in (0,1,2)

    with the indices :math:`p,l,d` representing the facet, line vector around
    the facet and and vector component, respectively.
    '''
    @tr.cached_property
    def _get_F_L_vectors_0(self):
        F_N = self.F_N  # F_N is cycled counter clockwise
        return self.x_0[F_N[:, (1, 2, 0)]] - self.x_0[F_N[:, (0, 1, 2)]]

    F_L_vectors = tr.Property(tr.Array, depends_on=INPUT)
    r'''Get the cycled line vectors around the facet
    The cycle is closed - the first and last vector are identical.


    .. math::
        v_{pld} \;\mathrm{where} \; p\in\mathcal{F}, l\in (0,1,2), d\in (0,1,2)

    with the indices :math:`p,l,d` representing the facet, line vector around
    the facet and and vector component, respectively.
    '''
    @tr.cached_property
    def _get_F_L_vectors(self):
        F_N = self.F_N  # F_N is cycled counter clockwise
        return self.x[F_N[:, (1, 2, 0)]] - self.x[F_N[:, (0, 1, 2)]]

    F_L_vectors_du = tr.Property(tr.Array, depends_on=INPUT)
    r'''Get the derivatives of the line vectors around the facets.

    .. math::
        \pard{v_{pld}}{x_{Ie}} \; \mathrm{where} \;
        p \in \mathcal{F},  \in (0,1,2), d\in (0,1,2), I\in \mathcal{N},
        e \in (0,1,3)

    with the indices :math:`p,l,d,I,e` representing the facet,
    line vector around the facet and and vector component,
    node vector and and its component index,
    respectively.

    This array works essentially as an index function delivering -1
    for the components of the first node in each dimension and +1
    for the components of the second node
    in each dimension.

    For a facet :math:`p` with lines :math:`l` and component :math:`d` return
    the derivatives with respect to the displacement of the node :math:`I`
    in the direction :math:`e`.

    .. math::
        \bm{a}_1 = \bm{x}_2 - \bm{x}_1 \\
        \bm{a}_2 = \bm{x}_3 - \bm{x}_2 \\
        \bm{a}_3 = \bm{x}_1 - \bm{x}_3

    The corresponding derivatives are then

    .. math::
        \pard{\bm{a}_1}{\bm{u}_1} = -1, \;\;\;
        \pard{\bm{a}_1}{\bm{u}_2} = 1 \\
        \pard{\bm{a}_2}{\bm{u}_2} = -1, \;\;\;
        \pard{\bm{a}_2}{\bm{u}_3} = 1 \\
        \pard{\bm{a}_3}{\bm{u}_3} = -1, \;\;\;
        \pard{\bm{a}_3}{\bm{u}_1} = 1 \\

    '''

    def _get_F_L_vectors_du(self):
        return self.L_vectors_du[self.F_L]

    F_L_vectors_dul = tr.Property(tr.Array, depends_on=INPUT)

    def _get_F_L_vectors_dul(self):
        return self.L_vectors_dul[self.F_L]

    norm_F_L_vectors = tr.Property(tr.Array, depends_on=INPUT)
    r'''Get the cycled line vectors around the facet
    The cycle is closed - the first and last vector are identical.
    '''
    @tr.cached_property
    def _get_norm_F_L_vectors(self):
        v = self.F_L_vectors
        mag_v = np.sqrt(np.einsum('...i,...i', v, v))
        return v / mag_v[..., np.newaxis]

    norm_F_L_vectors_du = tr.Property(tr.Array, depends_on=INPUT)
    '''Get the derivatives of cycled line vectors around the facet
    '''
    @tr.cached_property
    def _get_norm_F_L_vectors_du(self):
        v = self.F_L_vectors
        v_du = self.F_L_vectors_du  # @UnusedVariable
        mag_v = np.einsum('...i,...i', v, v)  # @UnusedVariable
        # @todo: finish the chain rule
        raise NotImplemented

    # =========================================================================
    # Orthonormal basis of each facet.
    # =========================================================================
    F_L_bases = tr.Property(tr.Array, depends_on=INPUT)
    r'''Line bases around a facet.
    '''
    @tr.cached_property
    def _get_F_L_bases(self):
        l = self.norm_F_L_vectors
        n = self.norm_F_normals
        lxn = np.einsum('...li,...j,...kij->...lk', l, n, EPS)
        n_ = n[:, np.newaxis, :] * np.ones((1, 3, 1), dtype='float_')
        T = np.concatenate([l[:, :, np.newaxis, :],
                            -lxn[:, :, np.newaxis, :],
                            n_[:, :, np.newaxis, :]], axis=2)
        return T

    F_L_bases_du = tr.Property(tr.Array, depends_on=INPUT)
    r'''Derivatives of the line bases around a facet.
    '''
    @tr.cached_property
    def _get_F_L_bases_du(self):
        '''Derivatives of line bases'''
        raise NotImplemented

    # =========================================================================
    # Sector angles
    # =========================================================================
    F_theta = tr.Property(tr.Array, depends_on=INPUT)
    '''Get the sector angles :math:`\theta`  within a facet.
    '''
    @tr.cached_property
    def _get_F_theta(self):
        v = self.F_L_vectors
        a = -v[:, (2, 0, 1), :]
        b = v[:, (0, 1, 2), :]
        return get_theta(a, b)

    F_theta_du = tr.Property(tr.Array, depends_on=INPUT)
    r'''Get the derivatives of sector angles :math:`\theta` within a facet.
    '''
    @tr.cached_property
    def _get_F_theta_du(self):
        v = self.F_L_vectors
        v_du = self.F_L_vectors_du

        a = -v[:, (2, 0, 1), :]
        b = v[:, (0, 1, 2), :]
        a_du = -v_du[:, (2, 0, 1), ...]
        b_du = v_du[:, (0, 1, 2), ...]

        return get_theta_du(a, a_du, b, b_du)

    Fa_normals_du = tr.Property
    '''Get the derivatives of the normals with respect
    to the node displacements.
    '''

    def _get_Fa_normals_du(self):
        x_F = self.x[self.F_N]
        N_deta_ip = self.Na_deta
        NN_delta_eps_x1 = np.einsum('aK,aL,KJ,dli,ILl->IaiJd',
                                    N_deta_ip[:, 0, :], N_deta_ip[:, 1, :],
                                    DELTA, EPS, x_F)
        NN_delta_eps_x2 = np.einsum('aK,aL,LJ,kdi,IKk->IaiJd',
                                    N_deta_ip[:, 0, :], N_deta_ip[:, 1, :],
                                    DELTA, EPS, x_F)
        n_du = NN_delta_eps_x1 + NN_delta_eps_x2
        return n_du

    Fa_area_du = tr.Property
    '''Get the derivatives of the facet area with respect
    to node displacements.
    '''

    def _get_Fa_area_du(self):
        a = self.Fa_area
        n = self.Fa_normals
        n_du = self.Fa_normals_du
        a_du = np.einsum('Ia,Iak,IakJd->IaJd', 1 / a, n, n_du)
        return a_du

    Fa_normals = tr.Property
    '''Get normals of the facets.
    '''

    def _get_Fa_normals(self):

        x_F = self.x[self.F_N]
        N_deta_ip = self.Na_deta
        r_deta = np.einsum('ajK,IKi->Iaij', N_deta_ip, x_F)
        return np.einsum('Iai,Iaj,ijk->Iak',
                         r_deta[..., 0], r_deta[..., 1], EPS)

    Fa_normals_0 = tr.Property
    '''Get normals of the facets.
    '''

    def _get_Fa_normals_0(self):
        x_F = self.x_0[self.F_N]
        N_deta_ip = self.Na_deta
        r_deta = np.einsum('ajK,IKi->Iaij', N_deta_ip, x_F)
        return np.einsum('Iai,Iaj,ijk->Iak',
                         r_deta[..., 0], r_deta[..., 1], EPS)

    Fa_area = tr.Property
    '''Get the surface area of the facets.
    '''

    def _get_Fa_area(self):
        n = self.Fa_normals
        a = np.sqrt(np.einsum('Iai,Iai->Ia', n, n))
        return a

    Fa_r = tr.Property
    '''Get the reference vector to integrations point in each facet.
    '''

    def _get_Fa_r(self):
        x_F = self.x[self.F_N]
        N_eta_ip = self.Na
        r = np.einsum('aK,IKi->Iai', N_eta_ip, x_F)
        return r

    # =========================================================================
    # Interier as level set
    # =========================================================================
