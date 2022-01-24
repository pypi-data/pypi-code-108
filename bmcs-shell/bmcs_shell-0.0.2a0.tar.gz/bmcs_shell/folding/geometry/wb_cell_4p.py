"""

"""
import bmcs_utils.api as bu
import sympy as sp
from bmcs_shell.folding.geometry.wb_cell import WBCell
from sympy.algebras.quaternion import Quaternion
import k3d
import traits.api as tr
import numpy as np


class WBElemSymb4Param(bu.SymbExpr):

    a, b, c = sp.symbols('a, b, c', positive=True)
    u_2, u_3 = sp.symbols('u_2, u_3', positive=True)
    alpha = sp.symbols('alpha', positive=True)

    U0_a = sp.Matrix([a, b, 0])
    W0_a = sp.Matrix([c, 0, 0])
    UW0_a = W0_a - U0_a
    L2_U_0 = (U0_a.T * U0_a)[0]
    L2_UW_0 = (UW0_a.T * UW0_a)[0]

    U1_a = sp.Matrix([a, u_2, u_3])
    W1_a = sp.Matrix([c * sp.cos(alpha), 0, c * sp.sin(alpha)])
    UW1_a = U1_a - W1_a
    L2_U_1 = (U1_a.T * U1_a)[0]
    L2_UW_1 = (UW1_a.T * UW1_a)[0]

    u2_sol = sp.solve(L2_U_1 - L2_U_0, u_2)[0]
    u3_sol = sp.solve((L2_UW_1 - L2_UW_0).subs(u_2, u2_sol), u_3)[0]
    u_3_ = u3_sol
    u_2_ = u2_sol.subs(u_3, u3_sol)

    U_pp_a = U1_a.subs({u_2: u_2_, u_3: u_3_})
    U_mm_a = sp.Matrix([-U_pp_a[0], -U_pp_a[1], U_pp_a[2]])
    U_mp_a = sp.Matrix([-U_pp_a[0], U_pp_a[1], U_pp_a[2]])
    U_pm_a = sp.Matrix([U_pp_a[0], -U_pp_a[1], U_pp_a[2]])
    W_p_a = W1_a.subs({u_2: u_2_, u_3: u_3_})
    W_m_a = sp.Matrix([-W_p_a[0], W_p_a[1], W_p_a[2]])

    V_UW = U_pp_a - W_p_a
    L_UW = sp.sqrt(V_UW[1] ** 2 + V_UW[2] ** 2)
    theta_sol = sp.simplify(2 * sp.asin(V_UW[2] / L_UW))

    theta = sp.Symbol(r'theta')
    q_theta = Quaternion.from_axis_angle([1, 0, 0], theta)

    d_1, d_2, d_3 = sp.symbols('d_1, d_2, d_3')
    D_a = sp.Matrix([d_1, d_2, d_3])
    UD_pp_a = U_pp_a + D_a
    WD_p_a = W_p_a + D_a
    d_subs = sp.solve(UD_pp_a - W_m_a, [d_1, d_2, d_3])

    # center of rotation
    UD_pp_a_ = UD_pp_a.subs(d_subs)
    # rotated point
    WD_p_a_ = WD_p_a.subs(d_subs)
    # pull back
    WD_p_a_pb = WD_p_a_ - UD_pp_a_
    # rotate using quaternion
    WD_p_a_rot = q_theta.rotate_point(WD_p_a_pb.T, q_theta)
    # push forward
    WD_p_a_pf = sp.Matrix(WD_p_a_rot) + UD_pp_a_
    # rotated compatibility point
    WD_p_a_theta = WD_p_a_pf.subs(theta, -theta_sol)

    # rotate the center of the neighbour cell
    DD_a_pb = D_a.subs(d_subs) - UD_pp_a_
    DD_a_rot = q_theta.rotate_point(DD_a_pb.T, q_theta)
    DD_a_pf = sp.simplify(sp.Matrix(DD_a_rot) + UD_pp_a_)
    DD_a_theta = DD_a_pf.subs(theta, -theta_sol)

    H = W_p_a[2]

    rho = (U_mm_a[2] - DD_a_theta[2]) / (U_mm_a[1] - DD_a_theta[1]) * U_mm_a[1]
    R_0 = U_mm_a[2] - rho
    delta_phi = sp.asin(DD_a_theta[1] / R_0)
    delta_x = a + W_p_a[0]

    # theta = sp.symbols('theta')
    # x_1, x_2, x_3 = sp.symbols('x_1, x_2, x_3')
    #
    # q_theta = Quaternion.from_axis_angle([1, 0, 0], theta)
    # X_rot = q_theta.rotate_point((x_1, x_2, x_3), q_theta)
    # X_theta_a = sp.simplify(sp.Matrix(X_rot))

    symb_model_params = ['alpha', 'a', 'b', 'c', ]
    symb_expressions = [
        ('u_2_', ()),
        ('u_3_', ()),
        ('R_0', ()),
        ('delta_phi', ()),
        ('delta_x', ()),
        ('H', ()),
        ('theta_sol', ())
    ]


class WBElem4Param(WBCell, bu.InjectSymbExpr):
    name = 'Waterbomb cell 4p'
    symb_class = WBElemSymb4Param

    plot_backend = 'k3d'

    alpha = bu.Float(1e-5, GEO=True)
    a = bu.Float(1000, GEO=True)
    b = bu.Float(1000, GEO=True)
    c = bu.Float(1000, GEO=True)
    a_high = bu.Float(2000)
    b_high = bu.Float(2000)
    c_high = bu.Float(2000)

    ipw_view = bu.View(
        bu.Item('alpha', latex=r'\alpha', editor=bu.FloatRangeEditor(
            low=1e-6, high=np.pi / 2, n_steps=100, continuous_update=True)),
        bu.Item('a', latex='a', editor=bu.FloatRangeEditor(
            low=1e-6, high_name='a_high', n_steps=100, continuous_update=True)),
        bu.Item('b', latex='b', editor=bu.FloatRangeEditor(
            low=1e-6, high_name='b_high', n_steps=100, continuous_update=True)),
        bu.Item('c', latex='c', editor=bu.FloatRangeEditor(
            low=1e-6, high_name='c_high', n_steps=100, continuous_update=True)),
        *WBCell.ipw_view.content,
    )

    n_I = tr.Property
    def _get_n_I(self):
        return len(self.X_Ia)

    X_Ia = tr.Property(depends_on='+GEO')
    '''Array with nodal coordinates I - node, a - dimension
    '''
    @tr.cached_property
    def _get_X_Ia(self):
        alpha = self.alpha
        u_2 = self.symb.get_u_2_()
        u_3 = self.symb.get_u_3_()
        return np.array([
            [0,0,0], # 0 point
            [self.a, u_2, u_3], #U++
            [-self.a, u_2, u_3], #U-+
            [self.a,-u_2, u_3], #U+-
            [-self.a,-u_2, u_3], #U--
            [self.c * np.cos(alpha), 0, self.c * np.sin(alpha)], # W0+
            [-self.c * np.cos(alpha), 0, self.c * np.sin(alpha)] # W0-
            ], dtype=np.float_
        )

    I_boundary = tr.Array(np.int_, value=[[2,1],
                                          [6,5],
                                          [4,3],])
    '''Boundary nodes in 2D array to allow for generation of shell boundary nodes'''

    X_theta_Ia = tr.Property(depends_on='+GEO')
    '''Array with nodal coordinates I - node, a - dimension
    '''
    @tr.cached_property
    def _get_X_theta_Ia(self):
        D_a = self.symb.get_D_(self.alpha).T
        theta = self.symb.get_theta_sol(self.alpha)
        XD_Ia = D_a + self.X_Ia
        X_center = XD_Ia[1,:]

        rotation_axes = np.array([[1, 0, 0]], dtype=np.float_)
        rotation_angles = np.array([-theta], dtype=np.float_)
        rotation_centers = np.array([X_center], dtype=np.float_)

        x_single = np.array([XD_Ia], dtype='f')
        x_pulled_back = x_single - rotation_centers[:, np.newaxis, :]
        q = axis_angle_to_q(rotation_axes, rotation_angles)
        x_rotated = qv_mult(q, x_pulled_back)
        x_pushed_forward = x_rotated + rotation_centers[:, np.newaxis, :]
        x_translated = x_pushed_forward #  + self.translations[:, np.newaxis, :]
        return x_translated[0,...]

    delta_x = tr.Property(depends_on='+GEO')
    @tr.cached_property
    def _get_delta_x(self):
        return self.symb.get_delta_x()

    delta_phi = tr.Property(depends_on='+GEO')
    @tr.cached_property
    def _get_delta_phi(self):
        return self.symb.get_delta_phi()

    R_0 = tr.Property(depends_on='+GEO')
    @tr.cached_property
    def _get_R_0(self):
        return self.symb.get_R_0()


def q_normalize(q, axis=1):
    sq = np.sqrt(np.sum(q * q, axis=axis))
    sq[np.where(sq == 0)] = 1.e-19
    return q / sq[:, np.newaxis]


def v_normalize(q, axis=1):
    sq = np.einsum('...a,...a->...', q, q)
    sq[np.where(sq == 0)] = 1.e-19
    return q / sq[..., np.newaxis]


def q_mult(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return np.array([w, x, y, z], dtype='f')


def q_conjugate(q):
    qn = q_normalize(q.T).T
    w, x, y, z = qn
    return np.array([w, -x, -y, -z], dtype='f')


def qv_mult(q1, u):
    #print('q1', q1.shape, 'u', u.shape)
    zero_re = np.zeros((u.shape[0], u.shape[1]), dtype='f')
    #print('zero_re', zero_re.shape)
    q2 = np.concatenate([zero_re[:, :, np.newaxis], u], axis=2)
    #print('q2', q2.shape)
    q2 = np.rollaxis(q2, 2)
    #print('q2', q2.shape)
    q12 = q_mult(q1[:, :, np.newaxis], q2[:, :, :])
    #print('q12', q12.shape)
    q_con = q_conjugate(q1)
    #print('q_con', q_con.shape)
    q = q_mult(q12, q_con[:, :, np.newaxis])
    #print('q', q.shape)
    q = np.rollaxis(np.rollaxis(q, 2), 2)
    #print('q', q.shape)
    return q[:, :, 1:]


def axis_angle_to_q(v, theta):
    v_ = v_normalize(v, axis=1)
    x, y, z = v_.T
#    print('x,y,z', x, y, z)
    theta = theta / 2
#    print('theta', theta)
    w = np.cos(theta)
    x = x * np.sin(theta)
    y = y * np.sin(theta)
    z = z * np.sin(theta)
#    print('x,y,z', x, y, z)
    return np.array([w, x, y, z], dtype='f')


def q_to_axis_angle(q):
    w, v = q[0, :], q[1:, :]
    theta = np.arccos(w) * 2.0
    return theta, v_normalize(v)

