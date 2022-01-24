
# from bmcs_shear.matmod.i_matmod import IMaterialModel
from bmcs_utils.api import View, Item, Float, FloatRangeEditor
import bmcs_utils.api as bu
import traits.api as tr
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from bmcs_cross_section.matmod import ConcreteMatMod

class ConcreteMaterialModelAdvExpr(bu.SymbExpr):
    # continue here
    w = sp.Symbol(r'w', real=True)
    s = sp.Symbol(r's', real = True)
    d_a, E_c = sp.symbols(r'd_a, E_c', nonnegative=True)
    f_t = sp.symbols(r'f_t', nonnegative=True)
    c_2 = sp.Symbol('c_2', nonnegative=True)
    c_1 = sp.Symbol('c_1', nonnegative=True)
    f_c = sp.Symbol('f_c', rnonnegative =True)
    a, b = sp.symbols(r'a, b', nonnegative = True)
    xi = sp.Symbol(r'\xi', nonnegative = True)
    sigma_z = sp.Symbol(r'\sigma_z', nonnegative = True)

    G_f = 0.028 * f_c ** 0.18 * d_a ** 0.32

    xi = sigma_z / f_c

    G_f_baz = (1 + (a/(1+b/xi)) - (1 + a + b)/(1 + b) * xi**8)

    L_c = E_c * G_f / f_t ** 2

    w_cr = f_t / E_c * L_c

    w_x = 5.14 * (G_f / f_t)

    # eps_cp = w_cr / L_c
    #
    # eps_p = w / L_c
    #
    # f_co = 2 * f_t

    #w_tc = 5.14 * G_f / f_t

    # f_ce = f_c * (1 / (0.8))

    r = s / w

    tau_0 = 0.25 * f_c

    a_3 = 2.45 / tau_0

    a_4 = 2.44 * (1 - (4 / tau_0))

    tau_s = sp.Piecewise(
        (0, w <= 0),
        (tau_0 * (1 - sp.sqrt((2 * w) / d_a)) * r * (a_3 + (a_4 * np.abs(r) ** 3)) / (1 + (a_4 * r ** 4)), w > 0)

    )

    tau_s_wal = sp.Piecewise(
        (0, w <= 0),
        ((- f_c / 30) + (1.8 * w**(-0.8) + (0.234 * w**(-0.707) - 0.2) * f_c ) * s, w > 0)
    )

    sigma_ag = sp.Piecewise(
        (0, w == w_cr),
        (-0.62 * sp.sqrt(w) * (r) / (1 + r ** 2) ** 0.25 * tau_s, w > w_cr)
    )
    #sp.Piecewise(
        #(0, w <= 0),
    #)

    f_w = f_t * sp.exp(-f_t * (w - w_cr) / G_f)

    sig_w = sp.Piecewise(
        (-f_c, E_c * w / L_c < -f_c),
        (E_c * w / L_c, w <= w_cr),
        #(f_w, w > w_cr)
        (f_w, sp.And(w > w_cr, w <= w_x)), #+ sigma_ag
        (sigma_ag, w > w_x)  #f_w == 0
    )

    d_sig_w = sig_w.diff(w)

    # sig_w = sp.Piecewise(
    #     (- f_c, w < - w_cr),
    #     (2 * f_t + (-f_c - 2 * f_t) * sp.sqrt(1 - ((w_cr - sp.Abs(w)) / (w_cr)) ** 2), w < 0),
    #     (E_c * w / L_c, w < w_cr),
    #     (f_t * (1 + ((c_1 * w) / (w_tc)) ** 3) * sp.exp((-c_2 * w) / (w_tc)) - (w / w_tc) * (1 + c_1 ** 3) * sp.exp(
    #         -c_2), w > w_cr)
    # )

    #sigma = sig_w + sigma_ag

    symb_model_params = ['d_a', 'E_c', 'f_t', 'c_1', 'c_2', 'f_c'] #'mu', 'chi' , 'a', 'b'

    symb_expressions = [('sig_w', ('w', 's',)),
                        ('tau_s', ('w', 's',)),
                        ('tau_s_wal', ('w', 's',))]

# @tr.provides(IMaterialModel)
class ConcreteMaterialModelAdv(ConcreteMatMod, bu.InjectSymbExpr):

    name = 'Concrete behavior'
    node_name = 'material model'

    symb_class = ConcreteMaterialModelAdvExpr

    d_a = Float(16, MAT=True)  ## dia of steel mm
    E_c = Float(28000, MAT=True)  ## tensile strength of Concrete in MPa
    f_t = Float(3, MAT=True)  ## Fracture Energy in N/m
    c_1 = Float(3, MAT=True)
    c_2 = Float(6.93, MAT=True)
    f_c = Float(33.3, MAT=True)
    L_fps = Float(50, MAT=True)
    a = Float(1.038, MAT=True)
    b = Float(0.245, MAT=True)
    interlock_factor = Float(1, MAT=True)

    ipw_view = View(
        Item('d_a', latex=r'd_a'),
        Item('E_c', latex=r'E_c'),
        Item('f_t', latex=r'f_t'),
        Item('f_c', latex=r'f_c'),
        Item('c_1', latex=r'c_1'),
        Item('c_2', latex=r'c_2'),
        Item('L_fps', latex=r'L_{fps}'),
        Item('a', latex = r'a'),
        Item('b', latex = r'b'),
        Item('interlock_factor', latex = r'\gamma_\mathrm{ag}', editor=FloatRangeEditor(low=0,high=1)),
        Item('w_cr', latex = r'w_\mathrm{cr}', readonly=True),
        Item('L_c', latex = r'L_\mathrm{c}', readonly=True),
        Item('G_f', latex=r'G_\mathrm{f}', readonly=True)
    )

    # G_f_baz = tr.Property(depends_on='_ITR, _INC, _GEO, _MAT, _DSC')
    # @tr.cached_property
    # def _get_G_f_baz(self):
    #     xi = self.sz_crack_tip_orientation.
    #     return self.symb.G_f_baz

    L_c = tr.Property(Float, depends_on='state_changed')
    @tr.cached_property
    def _get_L_c(self):
        return self.E_c * self.G_f / self.f_t**2

    w_cr = tr.Property(Float, depends_on='state_changed')
    @tr.cached_property
    def _get_w_cr(self):
        return (self.f_t / self.E_c) * self._get_L_c()


    G_f = tr.Property(Float, depends_on='state_changed')
    @tr.cached_property
    def _get_G_f(self):
        '''Calculating fracture energy
        '''
        return (0.028 * self.f_c ** 0.18 * self.d_a ** 0.32)

    def get_w_tc(self):
        '''Calculating point of softening curve resulting in 0 stress
        '''
        return ( 5.14 * self.G_f_baz / self.f_t)

    def get_sig_a(self, u_a): #w, s
        '''Calculating stresses
        '''
        sig_w = self.get_sig_w(u_a[...,0],u_a[...,1])
        tau_s = self.get_tau_s(u_a[...,0],u_a[...,1])
        return np.einsum('b...->...b', np.array([sig_w, tau_s], dtype=np.float_)) #, tau_s

    def get_sig_w(self,w, s):
        return self.symb.get_sig_w(w, s)

    def get_tau_s(self, w, s):
        return self.symb.get_tau_s(w, s) * self.interlock_factor

    w_min_factor = Float(1.2)
    w_max_factor = Float(15)
    def plot3d_sig_w(self, ax3d, vot=1.0):

        w_min = -(self.f_c / self.E_c * self._get_L_c()) * self.w_min_factor
        w_max = self.w_cr * self.w_max_factor
        w_range = np.linspace(w_min, w_max, 100)
        s_max = 3
        s_data = np.linspace(-1.1 * s_max, 1.1 * s_max, 100)
        s_, w_ = np.meshgrid(s_data, w_range)

        sig_w = self.get_sig_w(w_,s_)

        ax3d.plot_surface(w_, s_, sig_w, cmap='viridis', edgecolor='none')
        ax3d.set_xlabel(r'$w\;\;\mathrm{[mm]}$', fontsize=12)
        ax3d.set_ylabel(r'$s\;\;\mathrm{[mm]}$', fontsize=12)
        ax3d.set_zlabel(r'$\sigma_w\;\;\mathrm{[MPa]}$', fontsize=12)
        ax3d.set_title('crack opening law', fontsize=12)

    # def plot_sig_w(self, ax, vot=1.0):
    #         w_min = -(self.f_c / self.E_c * self._get_L_c()) * self.w_min_factor
    #         w_max = self.w_cr * self.w_max_factor
    #         w_range = np.linspace(w_min, w_max, 100)
    #         s_max = 3
    #         s_data = np.linspace(-1.1 * s_max, 1.1 * s_max, 100)
    #         sig_w = self.get_sig_w(w_range, s_data)
    #         ax.plot(w_range, sig_w, lw=2, color='red')
    #         ax.fill_between(w_range, sig_w,
    #                         color='red', alpha=0.2)
    #         ax.set_xlabel(r'$w\;\;\mathrm{[mm]}$', fontsize=12)
    #         ax.set_ylabel(r'$\sigma\;\;\mathrm{[MPa]}$', fontsize=12)
    #         ax.set_title('crack opening law', fontsize=12)

    def plot3d_tau_s(self, ax3d, vot=1.0):
        w_min = 1e-9 #-1
        w_max = 3
        w_data = np.linspace(w_min, w_max, 100)
        s_max = 3
        s_data = np.linspace(-1.1*s_max, 1.1*s_max, 100) #-1.1
        s_, w_ = np.meshgrid(s_data, w_data)
        tau_s = self.get_tau_s(w_, s_)
        ax3d.plot_surface(w_, s_, tau_s, cmap='viridis', edgecolor='none')
        ax3d.set_xlabel(r'$w\;\;\mathrm{[mm]}$', fontsize=12)
        ax3d.set_ylabel(r'$s\;\;\mathrm{[mm]}$', fontsize=12)
        ax3d.set_zlabel(r'$\tau\;\;\mathrm{[MPa]}$', fontsize=12)
        ax3d.set_title('aggregate interlock law', fontsize=12)

    # def subplots(self, fig):
    #     #ax_2d = fig.add_subplot(1, 2, 2)
    #     ax_3d_1 = fig.add_subplot(1, 2, 2, projection='3d')
    #     ax_3d_2 = fig.add_subplot(1, 2, 1, projection='3d')
    #     return ax_3d_1, ax_3d_2
    #
    # def update_plot(self, axes):
    #     '''Plotting function
    #     '''
    #     ax_3d_1, ax_3d_2 = axes
    #     self.plot3d_sig_w(ax_3d_1)
    #     self.plot3d_tau_s(ax_3d_2)

    def get_eps_plot_range(self):
        return np.linspace(1.1*self.eps_cu, 1.1*self.eps_tu,300)

    def get_sig(self,eps):
        return self.factor * self.symb.get_sig_w(eps)