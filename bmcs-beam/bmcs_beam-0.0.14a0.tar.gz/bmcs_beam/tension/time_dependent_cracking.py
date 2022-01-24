
import bmcs_utils.api as bu
import sympy as sp
import numpy as np
from scipy.integrate import cumtrapz

class TimeDependentCrackingExpr(bu.SymbExpr):

    t = sp.symbols('t', nonnegative=True)

    T_m = sp.Symbol("T_m", positive = True)
    T_s = sp.Symbol("T_s", positive = True)

    omega_fn = 1 - sp.exp(-(t / T_s) ** T_m)

    T_prime_0 = sp.Symbol("T_prime_0", positive=True)

    T_t = (1 - omega_fn) * T_prime_0 * t

    T_prime_t = sp.simplify(T_t.diff(t))

    t_argmax_T = sp.Symbol("t_argmax_T")
    T_s_sol = sp.solve(sp.Eq(sp.solve(T_prime_t, t)[0], t_argmax_T), T_s)[0]

    T_max = sp.Symbol("T_max", positive=True)
    T_prime_0_sol = sp.solve(sp.Eq(T_t.subs(T_s, T_s_sol).subs(t, t_argmax_T), T_max),
                             T_prime_0)[0]

    T_max_t = sp.simplify(T_t.subs({T_s: T_s_sol, T_prime_0: T_prime_0_sol}))
    dot_T_max_t = sp.simplify(T_max_t.diff(t))

    ## Time dependent compressive strength

    s = sp.Symbol("s", positive=True)

    beta_cc = sp.exp(s * (1 - sp.sqrt(28 / t)))

    f_cm_28 = sp.Symbol("f_cm28", positive=True)

    f_cm_t = beta_cc * f_cm_28

    f_ctm = sp.Symbol("f_ctm", positive=True)
    alpha_f = sp.Symbol("alpha_f", positive=True)
    f_ctm_t = beta_cc * f_ctm

    E_cm_28 = sp.Symbol("E_cm28", positive=True)
    E_cm_t = (f_cm_t / f_cm_28) ** 0.3 * E_cm_28
    dot_E_cm_t = E_cm_t.diff(t)

    alpha = sp.Symbol("alpha", positive=True)
    eps_eff_t = -alpha * T_max_t
    dot_eps_eff_t = -alpha * dot_T_max_t

    sig_t = E_cm_t * eps_eff_t
    dot_sig_t = sp.simplify(E_cm_t * dot_eps_eff_t) #  + dot_E_cm_t * eps_eff_t)

    symb_model_params = ['T_max', 't_argmax_T', 'T_m',
                         's', 'f_cm_28', 'f_ctm', 'alpha_f',
                         'E_cm_28', 'alpha']

    symb_expressions = [
        ('T_max_t', ('t',)),
        ('f_cm_t', ('t',)),
        ('f_ctm_t', ('t',)),
        ('E_cm_t', ('t',)),
        ('sig_t', ('t',)),
        ('dot_sig_t', ('t',))
    ]

class TimeDependentCracking(bu.InteractiveModel,bu.InjectSymbExpr):

    name = 'Time Dependent Cracking'

    symb_class = TimeDependentCrackingExpr

    T_m = bu.Float(1)
    T_max = bu.Float(45)
    t_argmax_T = bu.Float(1.4)
    s = bu.Float(0.2)
    f_cm_28 = bu.Float(30)
    f_ctm = bu.Float(4)
    alpha_f = bu.Float(1)
    E_cm_28 = bu.Float(28000)
    alpha = bu.Float(1e-5)
    t_max = bu.Float(10)

    ipw_view = bu.View(
        bu.Item('T_max', latex=r'T_{\max}',
                editor=bu.FloatRangeEditor(low=5,high=100,
                                           continuous_update=True)),
        bu.Item('t_argmax_T', latex='\mathrm{argmax} T',
                editor=bu.FloatRangeEditor(low=0.4,high=3,
                                           continuous_update=True)),
        bu.Item('T_m', latex='T_m',
                editor=bu.FloatRangeEditor(low=0.1,high=3,
                                           continuous_update=True)),
        bu.Item('s', latex='s'),
#        bu.Item('f_cm_28', latex=r'f_\mathrm{cm}^{28}'),
        bu.Item('f_ctm', latex=r'f_\mathrm{ctm}',
                editor=bu.FloatRangeEditor(low=3,high=10,
                                           continuous_update=True)),
        bu.Item('alpha_f', latex=r'\alpha_f'),
        bu.Item('E_cm_28', latex=r'E_\mathrm{cm}^{28}',
                editor=bu.FloatRangeEditor(low=25000,high=40000,
                                           continuous_update=True)),
        bu.Item('alpha', latex=r'\alpha'),
    )

    def subplots(self, fig):
        ax_sig = fig.subplots(1,1)
        ax_T = ax_sig.twinx()
        return ax_sig, ax_T

    def update_plot(self, axes):
        ax_sig, ax_T = axes
        t_range = np.linspace(1e-4,self.t_max,100)

        dot_sig_range = self.symb.get_dot_sig_t(t_range)
        sig2_range = cumtrapz(dot_sig_range,t_range,initial=0)
        ax_sig.plot(t_range, sig2_range, lw=2, color='green', label='$\sigma$')
        ax_sig.fill_between(t_range, sig2_range, 0, color='green', alpha=0.1)
        ax_sig.set_xlabel('$t$ [days]')
        ax_sig.set_ylabel('$\sigma$ [MPa]')

        f_ctm_range = self.symb.get_f_ctm_t(t_range)
        ax_sig.plot(t_range, f_ctm_range, lw=2, color='red', label='$f_\mathrm{ctm}$')
        ax_sig.fill_between(t_range, f_ctm_range, 0, color='red', alpha=0.05)
        ax_sig.legend()

        T_range = self.symb.get_T_max_t(t_range)
        ax_T.plot(t_range, T_range, color='blue',label='temperature')
        ax_T.fill_between(t_range, T_range, 0, color='blue', alpha=0.05)
        ax_T.set_ylabel('$T$ [C$^o$]')
        ax_T.legend()