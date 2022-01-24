import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import traits.api as tr
from scipy.optimize import root
from bmcs_utils.api import InteractiveModel


class ModelData(tr.HasStrictTraits):
    """This class holds all the data needed for the model, use the units [mm] - [N/mm^2] - [mm^2]"""

    # Geometry
    h = tr.Float(400)
    b = tr.Any(200)                   # Can be constant or sympy expression for the case of a varied b along height z

    # Concrete
    E_ct = tr.Float(24000)            # E modulus of concrete on tension
    E_cc = tr.Float(25000)            # E modulus of concrete on compression
    eps_cr = tr.Float(0.001)          # Concrete cracking strain
    eps_cy = tr.Float(-0.003)         # Concrete compressive yield strain
    eps_cu = tr.Float(-0.01)          # Ultimate concrete compressive strain
    eps_tu = tr.Float(0.003)          # Ultimate concrete tensile strain
    mu = tr.Float(0.33)               # Post crack tensile strength ratio (represents how much strength is left
                                      # after the crack because of short steel fibers in the mixture)

    # Reinforcement
    z_j = tr.Array(np.float_, value=[50])                         # z positions of reinforcement layers
    A_j = tr.Array(np.float_, value=[np.pi * (16 / 2.) ** 2])     # cross section area of reinforcement layers
    E_j = tr.Array(np.float_, value=[210000])                     # E modulus of reinforcement layers
    eps_sy_j = tr.Array(np.float_, value=[500. / 210000.])        # Steel yield strain


class MKappaSymbolic(tr.HasStrictTraits):
    """"This class handles all the symbolic calculations so that the class MomentCurvature doesn't use sympy ever"""

    # Sympy symbols definition
    E_ct, E_cc, eps_cr, eps_tu, mu = sp.symbols(r'E_ct, E_cc, varepsilon_cr, varepsilon_tu, mu', real=True,
                                                nonnegative=True)
    eps_cy, eps_cu = sp.symbols(r'varepsilon_cy, varepsilon_cu', real=True, nonpositive=True)
    kappa = sp.Symbol('kappa', real=True, nonpositive=True)
    eps_top = sp.symbols('varepsilon_top', real=True, nonpositive=True)
    eps_bot = sp.symbols('varepsilon_bot', real=True, nonnegative=True)
    b, h, z = sp.symbols('b, h, z', nonnegative=True)
    eps_sy, E_s = sp.symbols('varepsilon_sy, E_s')
    eps = sp.Symbol('varepsilon', real=True)

    # Sympy expressions
    eps_z_ = tr.Any
    subs_eps = tr.Any
    sig_c_z_lin = tr.Any
    sig_s_eps = tr.Any

    model_data = tr.Instance(ModelData)

    def _model_data_default(self):
        return ModelData()

    model_data_mapping = tr.Property

    def _get_model_data_mapping(self):
        # This is a mapping between each symbol and its numerical value so they can be used to get conciser symbolic
        # expressions later
        return {
            self.E_ct: self.model_data.E_ct,
            self.E_cc: self.model_data.E_cc,
            self.eps_cr: self.model_data.eps_cr,
            self.eps_cy: self.model_data.eps_cy,
            self.eps_cu: self.model_data.eps_cu,
            self.mu: self.model_data.mu,
            self.eps_tu: self.model_data.eps_tu
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Here all the symbolic expressions are prepared

        # Linear profile of strain over the cross section height
        self.eps_z_ = self.eps_bot + self.z * (self.eps_top - self.eps_bot) / self.h

        # Express varepsilon_top as a function of kappa and varepsilon_bot
        curvature_definition_ = self.kappa + self.eps_z_.diff(self.z)
        self.subs_eps = {self.eps_top: sp.solve(curvature_definition_, self.eps_top)[0]}
        # to return eps on a value z when (kappa, eps_bot) are given
        # get_eps_z = sp.lambdify((kappa, eps_bot, z), eps_z_.subs(subs_eps), 'numpy')

        # Concrete constitutive law
        sig_c_eps = sp.Piecewise(
            (0, self.eps < self.eps_cu),
            (self.E_cc * self.eps_cy, self.eps < self.eps_cy),
            (self.E_cc * self.eps, self.eps < 0),
            (self.E_ct * self.eps, self.eps < self.eps_cr),
            (self.mu * self.E_ct * self.eps_cr, self.eps < self.eps_tu),
            (0, self.eps >= self.eps_tu)
        )

        # Stress over the cross section height
        sig_c_z = sig_c_eps.subs(self.eps, self.eps_z_)

        # Substitute eps_top to get sig as a function of (kappa, eps_bot, z)
        self.sig_c_z_lin = sig_c_z.subs(self.subs_eps)

        # Reinforcement constitutive law
        self.sig_s_eps = sp.Piecewise(
            (-self.E_s * self.eps_sy, self.eps < -self.eps_sy),
            (self.E_s * self.eps, self.eps < self.eps_sy),
            (self.E_s * self.eps_sy, self.eps >= self.eps_sy)
        )

    get_b_z = tr.Property

    @tr.cached_property
    def _get_get_b_z(self):
        # If b is a constant number return a lambda function that always returns a constant "b" value
        # otherwise return a function that returns b_z values for each given z
        if isinstance(self.model_data.b, int) or isinstance(self.model_data.b, float):
            return lambda place_holder: self.model_data.b
        else:
            return sp.lambdify(self.z, self.model_data.b, 'numpy')

    # get_eps_z = tr.Property(depends_on='model_data_mapping_items')
    get_eps_z = tr.Property()

    @tr.cached_property
    def _get_get_eps_z(self):
        return sp.lambdify((self.kappa, self.eps_bot, self.z), self.eps_z_.subs(self.subs_eps), 'numpy')

    get_sig_c_z = tr.Property(depends_on='model_data_mapping_items')

    @tr.cached_property
    def _get_get_sig_c_z(self):
        return sp.lambdify((self.kappa, self.eps_bot, self.z), self.sig_c_z_lin.subs(self.model_data_mapping), 'numpy')

    # get_sig_s_eps = tr.Property(depends_on='model_data_mapping_items')
    get_sig_s_eps = tr.Property()

    @tr.cached_property
    def _get_get_sig_s_eps(self):
        return sp.lambdify((self.eps, self.E_s, self.eps_sy), self.sig_s_eps, 'numpy')


class MKappa(InteractiveModel):
    """Class returning the moment curvature relationship."""

    mcs = tr.Instance(MKappaSymbolic)

    def _mcs_default(self):
        return MKappaSymbolic()

    model_data = tr.DelegatesTo('mcs')

    # Number of material points along the height of the cross section
    n_m = tr.Int(100)

    z_m = tr.Property(depends_on='n_m, h')

    @tr.cached_property
    def _get_z_m(self):
        return np.linspace(0, self.model_data.h, self.n_m)

    kappa_range = tr.Tuple(-0.001, 0.001, 101)

    kappa_t = tr.Property(tr.Array(np.float_), depends_on='kappa_range')

    @tr.cached_property
    def _get_kappa_t(self):
        return np.linspace(*self.kappa_range)

    # Normal force
    def get_N_s_tj(self, kappa_t, eps_bot_t):
        eps_z_tj = self.mcs.get_eps_z(kappa_t[:, np.newaxis], eps_bot_t[:, np.newaxis],
                                      self.model_data.z_j[np.newaxis, :])
        sig_s_tj = self.mcs.get_sig_s_eps(eps_z_tj, self.model_data.E_j, self.model_data.eps_sy_j)
        return np.einsum('j,tj->tj', self.model_data.A_j, sig_s_tj)

    def get_N_c_t(self, kappa_t, eps_bot_t):
        z_tm = self.z_m[np.newaxis, :]
        b_z_m = self.mcs.get_b_z(z_tm)  # self.mcs.get_b_z(self.z_m) also OK
        N_z_tm = b_z_m * self.mcs.get_sig_c_z(kappa_t[:, np.newaxis], eps_bot_t[:, np.newaxis], z_tm)
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

    eps_cr = tr.Property()

    def _get_eps_cr(self):
        return np.array([self.model_data.eps_cr], dtype=np.float_)

    kappa_cr = tr.Property()

    def _get_kappa_cr(self):
        res = root(lambda kappa: self.get_N_t(kappa, self.eps_cr), 0.0000001 + np.zeros_like(self.eps_cr), tol=1e-10)
        return res.x

    # Bending moment

    M_s_t = tr.Property()

    def _get_M_s_t(self):
        eps_z_tj = self.mcs.get_eps_z(self.kappa_t[:, np.newaxis], self.eps_bot_t[:, np.newaxis],
                                      self.model_data.z_j[np.newaxis, :])
        sig_z_tj = self.mcs.get_sig_s_eps(eps_z_tj, self.model_data.E_j, self.model_data.eps_sy_j)
        return -np.einsum('j,tj,j->t', self.model_data.A_j, sig_z_tj, self.model_data.z_j)

    M_c_t = tr.Property()

    def _get_M_c_t(self):
        z_tm = self.z_m[np.newaxis, :]
        b_z_m = self.mcs.get_b_z(z_tm)
        N_z_tm = b_z_m * self.mcs.get_sig_c_z(self.kappa_t[:, np.newaxis], self.eps_bot_t[:, np.newaxis], z_tm)
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
        return self.mcs.get_sig_c_z(self.kappa_t[:, np.newaxis], self.eps_bot_t[:, np.newaxis],self.z_m[np.newaxis, :])

    idx = tr.Int(0)

    M_norm = tr.Property()

    def _get_M_norm(self):
        # Section modulus @TODO optimize W for var b
        W = (self.b * self.model_data.h ** 2) / 6
        sig_cr = self.model_data.E_ct * self.model_data.eps_cr
        return W * sig_cr

    kappa_norm = tr.Property()

    def _get_kappa_norm(self):
        return self.kappa_cr

    def get_kappa(self, M):
        """cut off the descending tails"""
        I_M = np.where(self.M_t[1:] - self.M_t[:-1] > 0)
        M_I = self.M_t[I_M]
        kappa_I = self.kappa_t[I_M]
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
        self._align_xaxis(ax2, ax3)

    M_scale = tr.Float(1e+6)

    def plot(self, ax1, ax2):
        idx = self.idx
        ax1.plot(self.kappa_t, self.M_t / self.M_scale)
        ax1.set_ylabel('Moment [kN.m]')
        ax1.set_xlabel('Curvature [$m^{-1}$]')
        ax1.plot(self.kappa_t[idx], self.M_t[idx] / self.M_scale, marker='o')
        ax2.barh(self.model_data.z_j, self.N_s_tj[idx, :], height=6, color='red', align='center')
        # ax2.plot(self.N_s_tj[idx, :], self.z_j, color='red')
        # print('Z', self.z_j)
        # print(self.N_s_tj[idx, :])
        # ax2.fill_between(eps_z_arr[idx,:], z_arr, 0, alpha=0.1);
        ax3 = ax2.twiny()
        #        ax3.plot(self.eps_tm[idx, :], self.z_m, color='k', linewidth=0.8)
        ax3.plot(self.sig_tm[idx, :], self.z_m)
        ax3.axvline(0, linewidth=0.8, color='k')
        ax3.fill_betweenx(self.z_m, self.sig_tm[idx, :], 0, alpha=0.1)
        self._align_xaxis(ax2, ax3)

    def _align_xaxis(self, ax1, ax2):
        """Align zeros of the two axes, zooming them out by same ratio"""
        axes = (ax1, ax2)
        extrema = [ax.get_xlim() for ax in axes]
        tops = [extr[1] / (extr[1] - extr[0]) for extr in extrema]
        # Ensure that plots (intervals) are ordered bottom to top:
        if tops[0] > tops[1]:
            axes, extrema, tops = [list(reversed(l)) for l in (axes, extrema, tops)]

        # How much would the plot overflow if we kept current zoom levels?
        tot_span = tops[1] + 1 - tops[0]

        b_new_t = extrema[0][0] + tot_span * (extrema[0][1] - extrema[0][0])
        t_new_b = extrema[1][1] - tot_span * (extrema[1][1] - extrema[1][0])
        axes[0].set_xlim(extrema[0][0], b_new_t)
        axes[1].set_xlim(t_new_b, extrema[1][1])

    def subplots(self, fig):
        return fig.subplots(1,2)

    def update_plot(self, axes):
        self.plot(*axes)

