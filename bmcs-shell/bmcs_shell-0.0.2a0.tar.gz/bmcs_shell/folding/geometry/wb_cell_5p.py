"""

"""
import bmcs_utils.api as bu
import sympy as sp
from bmcs_shell.folding.geometry.wb_cell import WBCell
from sympy.algebras.quaternion import Quaternion
import k3d
import traits.api as tr
import numpy as np
import math

def get_x_sol(Eq_UOU, x_ul, subs_yz):
    Eq_UOU_x = Eq_UOU.subs(subs_yz)
    Eq_UOU_x_rearr = sp.Eq(-Eq_UOU_x.args[1].args[1],
                           -Eq_UOU_x.args[0] + Eq_UOU_x.args[1].args[0] + Eq_UOU_x.args[1].args[2])
    Eq_UOU_x_rhs = Eq_UOU_x_rearr.args[1] ** 2 - Eq_UOU_x_rearr.args[0] ** 2
    Eq_UOU_x_rhs_collect = sp.collect(sp.expand(Eq_UOU_x_rhs), x_ul)

    A_ = Eq_UOU_x_rhs_collect.coeff(x_ul, 2)
    B_ = Eq_UOU_x_rhs_collect.coeff(x_ul, 1)
    C_ = Eq_UOU_x_rhs_collect.coeff(x_ul, 0)
    A, B, C = sp.symbols('A, B, C')

    x_ul_sol1, x_ul_sol2 = sp.solve(A * x_ul ** 2 + B * x_ul + C, x_ul)
    return x_ul_sol1, x_ul_sol2, A_, B_, C_


class WBElemSymb5ParamXL(bu.SymbExpr):

    a, b, c = sp.symbols('a, b, c', positive=True)
    gamma = sp.symbols('gamma')

    U_ur_0 = sp.Matrix([a, b, 0])
    U_ul_0 = sp.Matrix([-a, b, 0])
    V_r_0 = sp.Matrix([c, 0, 0])
    V_l_0 = sp.Matrix([-c, 0, 0])

    x_ur, y_ur, z_ur = sp.symbols(r'x_ur, y_ur, z_ur')
    x_ul, y_ul, z_ul = sp.symbols(r'x_ul, y_ul, z_ul')

    U_ur_1 = sp.Matrix([x_ur, y_ur, z_ur])
    U_ul_1 = sp.Matrix([x_ul, y_ul, z_ul])
    V_r_1 = sp.Matrix([c * sp.sin(gamma), 0, c * sp.cos(gamma)])
    V_l_1 = sp.Matrix([-c * sp.sin(gamma), 0, c * sp.cos(gamma)])
    X_UOV_r_0 = U_ur_0.T * V_r_0
    X_VOU_l_0 = U_ul_0.T * V_l_0
    X_UOV_r_1 = U_ur_1.T * V_r_1
    X_VOU_l_1 = U_ul_1.T * V_l_1
    Eq_UOV_r = sp.Eq(X_UOV_r_0[0], X_UOV_r_1[0])
    Eq_UOV_l = sp.Eq(X_VOU_l_0[0], X_VOU_l_1[0])
    X_VUO_r_0 = (V_r_0 - U_ur_0).T * (-U_ur_0)
    X_VUO_l_0 = (V_l_0 - U_ul_0).T * (-U_ul_0)
    X_VUO_r_1 = (V_r_1 - U_ur_1).T * (-U_ur_1)
    X_VUO_l_1 = (V_l_1 - U_ul_1).T * (-U_ul_1)
    Eq_VUO_r = sp.Eq(-X_VUO_r_0[0], -X_VUO_r_1[0])
    Eq_VUO_l = sp.Eq(-X_VUO_l_0[0], -X_VUO_l_1[0])

    X_UOU_0 = (U_ul_0).T * (U_ur_0)
    X_UOU_1 = (U_ul_1).T * (U_ur_1)
    Eq_UOU = sp.Eq(X_UOU_0[0], X_UOU_1[0])

    yz_ur_sol1, yz_ur_sol2 = sp.solve({Eq_UOV_r, Eq_VUO_r}, [y_ur, z_ur])
    yz_ul_sol1, yz_ul_sol2 = sp.solve({Eq_UOV_l, Eq_VUO_l}, [y_ul, z_ul])

    y_ur_sol1, z_ur_sol = yz_ur_sol1
    y_ul_sol1, z_ul_sol = yz_ul_sol1
    y_ur_sol2, _ = yz_ur_sol2
    y_ul_sol2, _ = yz_ul_sol2

    subs_yz1 = {y_ur: y_ur_sol1, z_ur: z_ur_sol,
               y_ul: y_ul_sol1, z_ul: z_ul_sol}
    subs_yz2 = {y_ur: y_ur_sol2, z_ur: z_ur_sol,
               y_ul: y_ul_sol2, z_ul: z_ul_sol}

    A, B, C = sp.symbols('A, B, C')
    x_ul_sol11, x_ul_sol12, A1_, B1_, C1_ = get_x_sol(Eq_UOU, x_ul, subs_yz1)
    x_ul_sol21, x_ul_sol22, A2_, B2_, C2_ = get_x_sol(Eq_UOU, x_ul, subs_yz2)

    x_ul11_ = x_ul_sol11
    x_ul12_ = x_ul_sol12
    x_ul21_ = x_ul_sol21
    x_ul22_ = x_ul_sol22
    y_ur1_ = y_ur_sol1
    y_ul1_ = y_ul_sol1
    y_ur2_ = y_ur_sol2
    y_ul2_ = y_ul_sol2
    z_ur_ = z_ur_sol
    z_ul_ = z_ul_sol

    P_1 = sp.sin(gamma) * x_ur - a
    P_2 = (x_ur - a * sp.sin(gamma))**2 - sp.cos(gamma)**2 * b**2
    P_3 = sp.sin(gamma) *(a**2+b**2) * x_ur - a * (a**2-b**2)

    symb_model_params = ['gamma', 'x_ur', 'a', 'b', 'c', ]
    symb_expressions = [
        ('x_ul11_', ('A', 'B', 'C')),
        ('x_ul12_', ('A', 'B', 'C')),
        ('x_ul21_', ('A', 'B', 'C')),
        ('x_ul22_', ('A', 'B', 'C')),
        ('y_ur1_', ('x_ul',)),
        ('y_ul1_', ('x_ul',)),
        ('y_ur2_', ('x_ul',)),
        ('y_ul2_', ('x_ul',)),
        ('z_ur_', ('x_ul',)),
        ('z_ul_', ('x_ul',)),
        ('A1_', ()),
        ('B1_', ()),
        ('C1_', ()),
        ('A2_', ()),
        ('B2_', ()),
        ('C2_', ()),
        ('V_r_1', ()),
        ('V_l_1', ()),
        ('P_1',()),
        ('P_2', ()),
        ('P_3', ()),
    ]

class WBElem5Param(WBCell, bu.InjectSymbExpr):
    name = 'waterbomb cell 5p'
    symb_class = WBElemSymb5ParamXL

    plot_backend = 'k3d'

    gamma = bu.Float(1, GEO=True)
    x_ur = bu.Float(1000, GEO=True)
    a = bu.Float(1000, GEO=True)
    b = bu.Float(1000, GEO=True)
    c = bu.Float(1000, GEO=True)
    a_low = bu.Float(2000)
    b_low = bu.Float(2000)
    c_low = bu.Float(2000)
    a_high = bu.Float(2000)
    b_high = bu.Float(2000)
    c_high = bu.Float(2000)
    y_sol1 = bu.Bool(False, GEO=True)
    x_sol1 = bu.Bool(False, GEO=True)

    continuous_update = True

    ipw_view = bu.View(
        bu.Item('gamma', latex=r'\gamma', editor=bu.FloatRangeEditor(
            low=1e-6, high=np.pi / 2, n_steps=100, continuous_update=continuous_update)),
        bu.Item('x_ur', latex=r'x^\urcorner', editor=bu.FloatRangeEditor(
            low=-2000, high=3000, n_steps=100, continuous_update=continuous_update)),
        bu.Item('a', latex='a', editor=bu.FloatRangeEditor(
            low=1e-6, high_name='a_high', n_steps=100, continuous_update=continuous_update)),
        bu.Item('b', latex='b', editor=bu.FloatRangeEditor(
            low=1e-6, high_name='b_high', n_steps=100, continuous_update=continuous_update)),
        bu.Item('c', latex='c', editor=bu.FloatRangeEditor(
            low=1e-6, high_name='c_high', n_steps=100, continuous_update=continuous_update)),
        bu.Item('y_sol1'),
        bu.Item('x_sol1'),
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
        gamma = self.gamma
        alpha = np.pi/2 - gamma

        P_1 = self.symb.get_P_1()
        P_2 = self.symb.get_P_2()
        P_3 = self.symb.get_P_3()

#        print('P', P_1, P_2, P_3, P_1*P_2*P_3)

        x_ur = self.x_ur

        if self.y_sol1:
            A = self.symb.get_A1_()
            B = self.symb.get_B1_()
            C = self.symb.get_C1_()
            if self.x_sol1:
                x_ul = self.symb.get_x_ul11_(A, B, C)
            else:
                x_ul = self.symb.get_x_ul12_(A, B, C)
            y_ul = self.symb.get_y_ul1_(x_ul)
            y_ur = self.symb.get_y_ur1_(x_ul)
        else:
            A = self.symb.get_A2_()
            B = self.symb.get_B2_()
            C = self.symb.get_C2_()
            if self.x_sol1:
                x_ul = self.symb.get_x_ul21_(A, B, C)
            else:
                x_ul = self.symb.get_x_ul22_(A, B, C)
            y_ul = self.symb.get_y_ul2_(x_ul)
            y_ur = self.symb.get_y_ur2_(x_ul)

        z_ur = self.symb.get_z_ur_(x_ul)
        z_ul = self.symb.get_z_ul_(x_ul)

        x_ll = -x_ur
        x_lr = -x_ul
        y_ll = - y_ur
        y_lr = - y_ul
        z_ll = z_ur
        z_lr = z_ul

        V_r_1 = self.symb.get_V_r_1().flatten()
        V_l_1 = self.symb.get_V_l_1().flatten()

        return np.array([
            [0,0,0], # 0 point
            [x_ur, y_ur, z_ur], #U++
            [x_ul, y_ul, z_ul], #U-+  ul
            [x_lr, y_lr, z_lr], #U+-
            [x_ll, y_ll, z_ll], #U--
            V_r_1, 
            V_l_1,
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

