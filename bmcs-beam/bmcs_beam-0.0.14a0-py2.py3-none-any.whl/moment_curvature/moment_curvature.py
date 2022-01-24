"""

"""
import numpy as np
import sympy as sp
import traits.api as tr
from bmcs_beam.beam_design.beam_design import BeamDesign
from scipy.optimize import root
from bmcs_utils.api import \
    InteractiveModel, Item, View, mpl_align_xaxis, \
    SymbExpr, InjectSymbExpr, Float, Int


class MomentCurvatureSymbolic(SymbExpr):
    """This class handles all the symbolic calculations
    so that the class MomentCurvature doesn't use sympy ever
    """
    #-------------------------------------------------------------------------
    # Symbolic derivation of expressions
    #-------------------------------------------------------------------------
    kappa = sp.Symbol('kappa', real=True)
    eps_top = sp.symbols('varepsilon_top', real=True)
    eps_bot = sp.symbols('varepsilon_bot', real=True)
    b, h, z = sp.symbols('b, h, z', nonnegative=True)
    eps_sy, E_s = sp.symbols('varepsilon_sy, E_s')
    eps = sp.Symbol('varepsilon', real=True)

    #-------------------------------------------------------------------------
    # Model parameters
    #-------------------------------------------------------------------------
    E_ct, E_cc, eps_cr, eps_tu, mu = sp.symbols(
        r'E_ct, E_cc, varepsilon_cr, varepsilon_tu, mu', real=True,
        nonnegative=True
    )
    eps_cy, eps_cu = sp.symbols(
        r'varepsilon_cy, varepsilon_cu',
        real=True, nonpositive=True
    )

    #-------------------------------------------------------------------------
    # Symbolic derivation of expressions
    #-------------------------------------------------------------------------
    # Linear profile of strain over the cross section height
    eps_z_ = eps_bot + z * (eps_top - eps_bot) / h
    eps_top_solved = {eps_top: sp.solve(kappa + eps_z_.diff(z), eps_top)[0]}
    eps_z = eps_z_.subs(eps_top_solved)

    sig_c_eps = sp.Piecewise(
        (0, eps < eps_cu),
        (E_cc * eps_cy, eps < eps_cy),
        (E_cc * eps, eps < 0),
        (E_ct * eps, eps < eps_cr),
        (mu * E_ct * eps_cr, eps < eps_tu),
        (0, eps >= eps_tu)
    )
    # Stress over the cross section height
    sig_c_z = sig_c_eps.subs(eps, eps_z)
    # sig_c_z = sig_c_eps.subs(eps, eps_z_) # this was like this originally

    # Substitute eps_top to get sig as a function of (kappa, eps_bot, z)
    sig_c_z = sig_c_z.subs(eps_top_solved)
    # Reinforcement constitutive law
    sig_s_eps = sp.Piecewise(
        (-E_s * eps_sy, eps < -eps_sy),
        (E_s * eps, eps < eps_sy),
        (E_s * eps_sy, eps >= eps_sy)
    )

    xget_b_z = tr.Property

    @tr.cached_property
    def _get_xget_b_z(self):
        # If b is a constant number return a lambda function that always returns a constant "b" value
        # otherwise return a function that returns b_z values for each given z
        if isinstance(self.model.b, int) or isinstance(self.model.b, float):
            return lambda place_holder: self.model.b
        else:
            return sp.lambdify(self.z, self.model.b, 'numpy')

    #----------------------------------------------------------------
    # SymbExpr protocol: Parameter names to be fetched from the model
    #----------------------------------------------------------------
    symb_model_params = ('E_ct', 'E_cc', 'eps_cr', 'eps_cy', 'eps_cu', 'mu', 'eps_tu')

    symb_expressions = [
        ('eps_z', ('kappa', 'eps_bot', 'z')),
        ('sig_c_z', ('kappa', 'eps_bot', 'z')),
        ('sig_s_eps', ('eps', 'E_s', 'eps_sy')),
    ]


class MomentCurvature(InteractiveModel, InjectSymbExpr):
    """Class returning the moment curvature relationship.
    """
    name = 'Moment-Curvature'
    ipw_view = View(
        Item('n_m', latex='n_m \mathrm{[mm]}', minmax=(1, 10000)),
        Item('idx')
    )

    symb_class = MomentCurvatureSymbolic
    beam_design = tr.Instance(BeamDesign, ())

    # Use PrototypedFrom only when the prototyped object is a class (The prototyped attribute behaves similarly
    # to a delegated attribute, until it is explicitly changed; from that point forward, the prototyped attribute
    # changes independently from its prototype.) (it's kind of like tr.DelegatesTo('beam_design.cross_section_shape'))
    cross_section_shape = tr.PrototypedFrom('beam_design', 'cross_section_shape')
    cross_section_layout = tr.PrototypedFrom('beam_design', 'cross_section_layout')
    matrix = tr.PrototypedFrom('cross_section_layout', 'matrix')
    reinforcement = tr.PrototypedFrom('cross_section_layout', 'reinforcement')

    # Geometry
    H = tr.DelegatesTo('cross_section_shape')
    # b = tr.DelegatesTo('cross_section_shape')

    # Concrete
    E_ct = tr.DelegatesTo('matrix')
    E_cc = tr.DelegatesTo('matrix')
    eps_cr = tr.DelegatesTo('matrix')
    eps_cy = tr.DelegatesTo('matrix')
    eps_cu = tr.DelegatesTo('matrix')
    eps_tu = tr.DelegatesTo('matrix')
    mu = tr.DelegatesTo('matrix')

    # Reinforcement
    z_j = tr.DelegatesTo('reinforcement')
    A_j = tr.DelegatesTo('reinforcement')
    E_j = tr.DelegatesTo('reinforcement')
    eps_sy_j = tr.DelegatesTo('reinforcement')

    n_m = Int(100)

    z_m = tr.Property(depends_on='n_m, h')

    @tr.cached_property
    def _get_z_m(self):
        return np.linspace(0, self.H, self.n_m)

    kappa_range = tr.Tuple(-0.001, 0.001, 101)

    kappa_t = tr.Property(tr.Array(np.float_), depends_on='kappa_range')

    @tr.cached_property
    def _get_kappa_t(self):
        return np.linspace(*self.kappa_range)

    # Normal force
    def get_N_s_tj(self, kappa_t, eps_bot_t):
        eps_z_tj = self.symb.get_eps_z(
            kappa_t[:, np.newaxis], eps_bot_t[:, np.newaxis],
            self.z_j[np.newaxis, :]
        )
        sig_s_tj = self.symb.get_sig_s_eps(
            eps_z_tj, self.E_j, self.eps_sy_j
        )
        N_s_tj = np.einsum('j,tj->tj', self.A_j, sig_s_tj)
        return N_s_tj

    def get_N_c_t(self, kappa_t, eps_bot_t):
        z_tm = self.z_m[np.newaxis, :]
        b_z_m = self.cross_section_shape.get_b(z_tm)
        N_z_tm = b_z_m * self.symb.get_sig_c_z(
            kappa_t[:, np.newaxis], eps_bot_t[:, np.newaxis], z_tm
        )
        return np.trapz(N_z_tm, x=z_tm, axis=-1)

    def get_N_t(self, kappa_t, eps_bot_t):
        N_s_t = np.sum(self.get_N_s_tj(kappa_t, eps_bot_t), axis=-1)
        return self.get_N_c_t(kappa_t, eps_bot_t) + N_s_t

    # SOLVER: Get eps_bot to render zero force

    eps_bot_t = tr.Property()
    r'''Resolve the tensile strain to get zero normal force for the prescribed curvature'''

    def _get_eps_bot_t(self):
        res = root(lambda eps_bot_t: self.get_N_t(self.kappa_t, eps_bot_t),
                   0.0000001 + np.zeros_like(self.kappa_t), tol=1e-6)
        return res.x

    # POSTPROCESSING

    kappa_cr = tr.Property()
    '''Curvature at which a critical strain is attained at the eps_bot'''
    def _get_kappa_cr(self):
        res = root(lambda kappa: self.get_N_t(kappa, self.eps_cr),
                   0.0000001 + np.zeros_like(self.eps_cr), tol=1e-10)
        return res.x

    # Bending moment

    M_s_t = tr.Property()

    def _get_M_s_t(self):
        eps_z_tj = self.symb.get_eps_z(
            self.kappa_t[:, np.newaxis], self.eps_bot_t[:, np.newaxis],
            self.z_j[np.newaxis, :]
        )
        sig_z_tj = self.symb.get_sig_s_eps(
            eps_z_tj, self.E_j, self.eps_sy_j
        )
        return -np.einsum('j,tj,j->t', self.A_j, sig_z_tj, self.z_j)

    M_c_t = tr.Property()

    def _get_M_c_t(self):
        z_tm = self.z_m[np.newaxis, :]
        b_z_m = self.cross_section_shape.get_b(z_tm)
        N_z_tm = b_z_m * self.symb.get_sig_c_z(
            self.kappa_t[:, np.newaxis], self.eps_bot_t[:, np.newaxis], z_tm
        )
        return -np.trapz(N_z_tm * z_tm, x=z_tm, axis=-1)

    M_t = tr.Property()

    def _get_M_t(self):
        return self.M_c_t + self.M_s_t

    N_s_tj = tr.Property()

    def _get_N_s_tj(self):
        return self.get_N_s_tj(self.kappa_t, self.eps_bot_t)

    eps_tm = tr.Property()

    def _get_eps_tm(self):
        return self.get_eps_z(self.kappa_t[:, np.newaxis], self.eps_bot_t[:, np.newaxis], self.z_m[np.newaxis, :])

    sig_tm = tr.Property()

    def _get_sig_tm(self):
        return self.symb.get_sig_c_z(
            self.kappa_t[:, np.newaxis], self.eps_bot_t[:, np.newaxis],self.z_m[np.newaxis, :]
        )

    idx = Int(0)

    M_norm = tr.Property()

    def _get_M_norm(self):
        # Section modulus @TODO optimize W for var b
        W = (self.b * self.H ** 2) / 6
        sig_cr = self.E_ct * self.eps_cr
        return W * sig_cr

    kappa_norm = tr.Property()

    def _get_kappa_norm(self):
        return self.kappa_cr

    M_kappa_data = tr.Property()
    def _get_M_kappa_data(self):
        """cut off the descending tails"""
        
        M_t = self.M_t #(the negative sign ---> returns empty M_I and kappa_I
        I_max = np.argmax(M_t)
        I_min = np.argmin(M_t)
        M_I = self.M_t[I_min:I_max]
        kappa_I = self.kappa_t[I_min:I_max]
        return M_I, kappa_I

    """ get_kappa from moment_curvature_.py"""
#         I_M = np.where(self.M_t[1:] - self.M_t[:-1] > 0)
#         M_I = self.M_t[I_M]
#         kappa_I = self.kappa_t[I_M]
#         return M_I, kappa_I

    def get_kappa(self, M):
        M_I, kappa_I = self.M_kappa_data
        return np.interp(M, M_I, kappa_I)

    def plot_norm(self, ax1, ax2):
        idx = self.idx
        ax1.plot(self.kappa_t / self.kappa_norm, self.M_t / self.M_norm)
        ax1.plot(self.kappa_t[idx] / self.kappa_norm, self.M_t[idx] / self.M_norm, marker='o')
        ax2.barh(self.z_j, self.N_s_tj[idx, :], height=2, color='red', align='center')
        # ax2.fill_between(eps_z_arr[idx,:], z_arr, 0, alpha=0.1);
        ax3 = ax2.twiny()
        #        ax3.plot(self.eps_tm[idx, :], self.z_m, color='k', linewidth=0.8)
        ax3.plot(self.sig_tm[idx, :], self.z_m)
        ax3.axvline(0, linewidth=0.8, color='k')
        ax3.fill_betweenx(self.z_m, self.sig_tm[idx, :], 0, alpha=0.1)
        mpl_align_xaxis(ax2, ax3)

    M_scale = Float(1e+6)

    def plot(self, ax1, ax2, ax3):
        idx = self.idx
        ax1.plot(self.kappa_t, self.M_t / self.M_scale)
        ax1.set_ylabel('Moment [kN.m]')
        ax1.set_xlabel('Curvature [$m^{-1}$]')
        ax1.plot(self.kappa_t[idx], self.M_t[idx] / self.M_scale, marker='o')
        ax2.barh(self.z_j, self.N_s_tj[idx, :], height=6, color='red', align='center')
        # ax2.plot(self.N_s_tj[idx, :], self.z_j, color='red')
        # print('Z', self.z_j)
        # print(self.N_s_tj[idx, :])
        # ax2.fill_between(eps_z_arr[idx,:], z_arr, 0, alpha=0.1);
        #        ax3.plot(self.eps_tm[idx, :], self.z_m, color='k', linewidth=0.8)
        ax3.plot(self.sig_tm[idx, :], self.z_m)
        ax3.axvline(0, linewidth=0.8, color='k')
        ax3.fill_betweenx(self.z_m, self.sig_tm[idx, :], 0, alpha=0.1)
        mpl_align_xaxis(ax2, ax3)

    def subplots(self, fig):
        ax1, ax2 = fig.subplots(1,2)
        ax3 = ax2.twiny()
        return ax1, ax2, ax3

    def update_plot(self, axes):
        self.plot(*axes)

if __name__ == '__main__':
    mc = MomentCurvature(
        kappa_range = (-0.0002, 0.0002, 100),
        idx=25, n_m=100
    )
    import matplotlib.pyplot as plt

    if False:

        # If plot_norm is used, use the following:
        # mc.kappa_range = (0, mc.kappa_cr * 100, 100)
        fig, ((ax1, ax2)) = plt.subplots(1, 2, figsize=(10, 5))
        mc.plot(ax1, ax2)
        plt.show()

    # Test getting kappa by providing Moment values
    if True:

        # Plotting
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        ax1.plot(mc.kappa_t, mc.M_t)
        ax2.plot(*mc.M_kappa_data)
        plt.show()
