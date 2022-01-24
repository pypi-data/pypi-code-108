

import bmcs_utils.api as bu
import numpy as np
import sympy as sp
import traits.api as tr

class PO_ELF_RLM_Symb(bu.SymbExpr):
    """Pullout of elastic Long fiber, fromm rigid long matrix
    """
    E_f, A_f = sp.symbols(r'E_\mathrm{f}, A_\mathrm{f}', positive=True)
    E_m, A_m = sp.symbols(r'E_\mathrm{m}, A_\mathrm{m}', positive=True)
    tau, p = sp.symbols(r'\bar{\tau}, p', positive=True)
    C, D = sp.symbols(r'C, D')
    P, w = sp.symbols(r'P, w', positive=True)
    x, a, L_b = sp.symbols(r'x, a, L_b')

    d_sig_f = p * tau / A_f

    sig_f = sp.integrate(d_sig_f, x) + C
    eps_f = sig_f / E_f

    u_f = sp.integrate(eps_f, x) + D

    eq_C = {P - sig_f.subs({x:0}) * A_f}
    C_subs = sp.solve(eq_C,C)

    eqns_D = {u_f.subs(C_subs).subs(x, a)}
    D_subs = sp.solve(eqns_D, D)

    u_f.subs(C_subs).subs(D_subs)
    eqns_a = {eps_f.subs(C_subs).subs(D_subs).subs(x, a)}
    a_subs = sp.solve(eqns_a, a)

    var_subs = {**C_subs,**D_subs,**a_subs}

    u_f_x = u_f.subs(var_subs)

    u_fa_x = sp.Piecewise((u_f_x, x > var_subs[a]),
                          (0, x <= var_subs[a]))

    eps_f_x = sp.diff(u_fa_x,x)

    sig_f_x = E_f * eps_f_x

    tau_x = sp.simplify(sig_f_x.diff(x) * A_f / p)

    u_f_x.subs(x, 0) - w

    Pw_pull = sp.solve(u_f_x.subs({x: 0}) - w, P)[0]

    w_L_b = u_fa_x.subs(x, -L_b).subs(P, Pw_pull)

    aw_pull = a_subs[a].subs(P, Pw_pull)

    eps_m_x = eps_f_x * 1e-8
    sig_m_x = sig_f_x * 1e-8
    u_ma_x = u_fa_x * 1e-8
    #-------------------------------------------------------------------------
    # Declaration of the lambdified methods
    #-------------------------------------------------------------------------

    symb_model_params = ['E_f', 'A_f', 'tau', 'p', 'L_b']

    symb_expressions = [
        ('eps_f_x', ('x','P',)),
        ('eps_m_x', ('x','P',)),
        ('sig_f_x', ('x','P',)),
        ('sig_m_x', ('x','P',)),
        ('tau_x', ('x','P',)),
        ('u_fa_x', ('x','P',)),
        ('u_ma_x', ('x','P',)),
        ('w_L_b', ('w',)),
        ('aw_pull', ('w',)),
        ('Pw_pull', ('w',)),
    ]

class PO_ELF_ELM_Symb(bu.SymbExpr):
    """Pullout of elastic Long fiber, fromm elastic long matrix
    """
    E_m, A_m = sp.symbols(r'E_\mathrm{m}, A_\mathrm{m}', nonnegative=True)
    E_f, A_f = sp.symbols(r'E_\mathrm{f}, A_\mathrm{f}', nonnegative=True)
    tau, p = sp.symbols(r'\bar{\tau}, p', nonnegative=True)
    C, D, E, F = sp.symbols('C, D, E, F')
    P, w = sp.symbols('P, w')
    x, a, L_b = sp.symbols('x, a, L_b')

    d_sig_f = p * tau / A_f
    d_sig_m = -p * tau / A_m

    sig_f = sp.integrate(d_sig_f, x) + C
    sig_m = sp.integrate(d_sig_m, x) + D

    eps_f = sig_f / E_f
    eps_m = sig_m / E_m

    u_f = sp.integrate(eps_f, x) + E
    u_m = sp.integrate(eps_m, x) + F

    eq_C = {P - sig_f.subs({x: 0}) * A_f}
    C_subs = sp.solve(eq_C, C)
    eq_D = {P + sig_m.subs({x: 0}) * A_m}
    D_subs = sp.solve(eq_D, D)

    F_subs = sp.solve({u_m.subs(x, 0) - 0}, F)

    eqns_u_equal = {u_f.subs(C_subs).subs(x, a) - u_m.subs(D_subs).subs(F_subs).subs(x, a)}
    E_subs = sp.solve(eqns_u_equal, E)

    eqns_eps_equal = {eps_f.subs(C_subs).subs(x, a) - eps_m.subs(D_subs).subs(x, a)}
    a_subs = sp.solve(eqns_eps_equal, a)
    var_subs = {**C_subs, **D_subs, **F_subs, **E_subs, **a_subs}

    u_f_x = u_f.subs(var_subs)
    u_m_x = u_m.subs(var_subs)

    u_fa_x = sp.Piecewise((u_f_x.subs(x, var_subs[a]), x <= var_subs[a]),
                          (u_f_x, x > var_subs[a]))
    u_ma_x = sp.Piecewise((u_m_x.subs(x, var_subs[a]), x <= var_subs[a]),
                          (u_m_x, x > var_subs[a]))

    eps_f_x = sp.diff(u_fa_x, x)
    eps_m_x = sp.diff(u_ma_x, x)

    sig_f_x = E_f * eps_f_x
    sig_m_x = E_m * eps_m_x

    tau_x = sig_f_x.diff(x) * A_f / p

    eps_f_0 = P / E_f / A_f
    eps_m_0 = -P / E_m / A_m
    a_subs = sp.solve({P - p * tau * a}, a)
    w_el = sp.Rational(1, 2) * (eps_f_0 - eps_m_0) * a
    Pw_pull_elastic = sp.solve(w_el.subs(a_subs) - w, P)[1]

    Pw_push, Pw_pull = sp.solve(u_f_x.subs({x: 0}) - w, P)

    w_L_b = u_fa_x.subs(x, -L_b).subs(P, Pw_pull)

    aw_pull = a_subs[a].subs(P, Pw_pull)

    #-------------------------------------------------------------------------
    # Declaration of the lambdified methods
    #-------------------------------------------------------------------------

    symb_model_params = ['E_f', 'A_f', 'E_m', 'A_m', 'tau', 'p', 'L_b']

    symb_expressions = [
        ('eps_f_x', ('x','P',)),
        ('eps_m_x', ('x','P',)),
        ('sig_f_x', ('x','P',)),
        ('sig_m_x', ('x','P',)),
        ('tau_x', ('x','P',)),
        ('u_fa_x', ('x','P',)),
        ('u_ma_x', ('x','P',)),
        ('w_L_b', ('w',)),
        ('aw_pull', ('w',)),
        ('Pw_pull', ('w',)),
    ]

class PO_ESF_RLM_Symb(PO_ELF_RLM_Symb):

    E_f, A_f = sp.symbols(r'E_\mathrm{f}, A_\mathrm{f}', positive=True)
    E_m, A_m = sp.symbols(r'E_\mathrm{m}, A_\mathrm{m}', positive=True)
    tau, p = sp.symbols(r'\bar{\tau}, p', positive=True)
    C, D = sp.symbols(r'C, D')
    P, w = sp.symbols(r'P, w', positive=True)
    x, a, L_b = sp.symbols(r'x, a, L_b')

    d_sig_f = p * tau / A_f

    sig_f = sp.integrate(d_sig_f, x) + C
    eps_f = sig_f / E_f

    u_f = sp.integrate(eps_f, x) + D

    eq_C = {P - sig_f.subs({x:0}) * A_f}
    C_subs = sp.solve(eq_C,C)

    eqns_D = {u_f.subs(C_subs).subs(x, a)}
    D_subs = sp.solve(eqns_D, D)

    u_f.subs(C_subs).subs(D_subs)
    eqns_a = {eps_f.subs(C_subs).subs(D_subs).subs(x, a)}
    a_subs = sp.solve(eqns_a, a)

    var_subs = {**C_subs,**D_subs,**a_subs}

    u_f_x = u_f.subs(var_subs)

    u_fa_x = sp.Piecewise((u_f_x, x > var_subs[a]),
                          (0, x <= var_subs[a]))

    eps_f_x = sp.diff(u_fa_x,x)

    sig_f_x = E_f * eps_f_x

    tau_x = sp.simplify(sig_f_x.diff(x) * A_f / p)

    u_f_x.subs(x, 0) - w

    Pw_pull = sp.solve(u_f_x.subs({x: 0}) - w, P)[0]

    w_L_b = u_fa_x.subs(x, -L_b).subs(P, Pw_pull)

    aw_pull = a_subs[a].subs(P, Pw_pull)

    eps_m_x = eps_f_x * 1e-8
    sig_m_x = sig_f_x * 1e-8
    u_ma_x = u_fa_x * 1e-8

    P_max = p * tau * L_b
    w_argmax = sp.solve(P_max - Pw_pull, w)[0]
    Pw_up_pull = Pw_pull
    b, P_down = sp.symbols(r'b, P_\mathrm{down}')
    sig_down = P_down / A_f
    eps_down = 1 / E_f * sig_down
    w_down = (L_b + b) - sp.Rational(1, 2) * eps_down * b
    Pw_down_pull, Pw_down_push = sp.solve(
        w_down.subs(b, -P_down / p / tau) - w,
        P_down
    )
    Pw_short = sp.Piecewise((0, w <= 0),
                            (Pw_up_pull, w <= w_argmax),
                            (Pw_down_pull, w <= L_b),
                            (0, True)
                           )
    w_L_b_a = L_b - Pw_down_pull / p / tau
    w_L_b = sp.Piecewise((0, w <= w_argmax),
                         (w_L_b_a, (w > w_argmax) & (w <= L_b)),
                         (w, True))
    aw_pull = - (Pw_short / p / tau)
    Pw_pull = Pw_short

    #-------------------------------------------------------------------------
    # Declaration of the lambdified methods
    #-------------------------------------------------------------------------

    symb_model_params = ['E_f', 'A_f', 'E_m', 'A_m', 'tau', 'p', 'L_b']

    symb_expressions = [
        ('eps_f_x', ('x','P',)),
        ('eps_m_x', ('x','P',)),
        ('sig_f_x', ('x','P',)),
        ('sig_m_x', ('x','P',)),
        ('tau_x', ('x','P',)),
        ('u_fa_x', ('x','P',)),
        ('u_ma_x', ('x','P',)),
        ('w_L_b', ('w',)),
        ('aw_pull', ('w',)),
        ('Pw_pull', ('w',)),
    ]


class PullOutAModel(bu.Model, bu.InjectSymbExpr):
    """
    Pullout elastic long fiber and rigid long matrix
    """
    symb_class = PO_ESF_RLM_Symb

    name = "Pull-Out"

    E_f = bu.Float(210000, MAT=True)
    E_m = bu.Float(28000, MAT=True)
    tau = bu.Float(8, MAT=True)
    A_f = bu.Float(100, CS=True)
    A_m = bu.Float(100*100, CS=True)
    p = bu.Float(20, CS=True)
    L_b = bu.Float(300, GEO=True)
    w_max = bu.Float(3, BC=True)

    t = bu.Float(0.0)
    t_max = bu.Float(1.0)

    ipw_view = bu.View(
        bu.Item('E_f', latex=r'E_\mathrm{f}~[\mathrm{MPa}]'),
        bu.Item('E_m', latex=r'E_\mathrm{m}~[\mathrm{MPa}]'),
        bu.Item('tau', latex=r'\tau~[\mathrm{MPa}]'),
        bu.Item('A_f', latex=r'A_\mathrm{f}~[\mathrm{mm}^2]'),
        bu.Item('A_m', latex=r'A_\mathrm{m}~[\mathrm{mm}^2]'),
        bu.Item('p', latex=r'p~[\mathrm{mm}]'),
        bu.Item('L_b', latex=r'L_\mathrm{b}~[\mathrm{mm}]'),
        bu.Item('w_max', latex=r'w_\max~[\mathrm{mm}]'),
        time_editor = bu.HistoryEditor(
            var='t',
            var_max='t_max'
        )
    )

    w_range = tr.Property(depends_on='state_changed')
    """Pull-out range w"""
    @tr.cached_property
    def _get_w_range(self):
        return np.linspace(0, self.w_max, 100)

    def plot_fields(self, ax11, ax12, ax21, ax22):
        L_b = self.L_b
        x_range = np.linspace(-L_b, 0, 100)
        w_max = self.w_max
        w = self.t * w_max
        P = self.symb.get_Pw_pull(w)
        eps_f_range = self.symb.get_eps_f_x(x_range, P)
        sig_f_range = self.symb.get_sig_f_x(x_range, P)
        u_f_range = self.symb.get_u_fa_x(x_range, P)
        eps_m_range = self.symb.get_eps_m_x(x_range, P)
        sig_m_range = self.symb.get_sig_m_x(x_range, P)
        u_m_range = self.symb.get_u_ma_x(x_range, P)
        tau_range = self.symb.get_tau_x(x_range, P)

        P_max = self.symb.get_Pw_pull(w_max)
        eps_f_max = self.symb.get_eps_f_x(0, P_max)
        sig_f_max = self.symb.get_sig_f_x(0, P_max)
        u_f_max = self.symb.get_u_fa_x(0, P_max)
        eps_m_max = self.symb.get_eps_m_x(0, P_max)
        sig_m_max = self.symb.get_sig_m_x(0, P_max)
        u_m_max = self.symb.get_u_ma_x(0, P_max)
        tau_max = self.symb.get_tau_x(0, P_max)

        ax11.plot(x_range, eps_f_range, color='blue')
        ax11.plot(x_range, eps_m_range, color='blue', linestyle='dashed')
        ax11.fill_between(x_range, eps_f_range, 0, color='blue', alpha=0.1)
        ax11.fill_between(x_range, eps_m_range, 0, color='blue', alpha=0.1)
        ax11.set_xlabel(r'$x$ [mm]')
        ax11.set_ylabel(r'$\varepsilon$ [-]')
        ax11.set_ylim(ymin=eps_m_max,ymax=eps_f_max)

        ax21.plot(x_range, sig_f_range, color='red')
        ax21.plot(x_range, sig_m_range, color='red', linestyle='dashed')
        ax21.fill_between(x_range, sig_f_range, 0, alpha=0.1, color='red')
        ax21.fill_between(x_range, sig_m_range, 0, alpha=0.1, color='red')
        ax21.set_xlabel(r'$x$ [mm]')
        ax21.set_ylabel(r'$\sigma$ [MPa]')
        ax21.set_ylim(ymin=sig_m_max,ymax=sig_f_max)

        ax12.plot(x_range, u_f_range, color='green')
        ax12.plot(x_range, u_m_range, color='green', linestyle='dashed')
        ax12.fill_between(x_range, u_f_range, 0, alpha=0.1, color='green')
        ax12.fill_between(x_range, u_m_range, 0, alpha=0.1, color='green')
        ax12.set_xlabel(r'$x$ [mm]')
        ax12.set_ylabel(r'$u$ [mm]')
        ax12.set_ylim(ymin=u_m_max,ymax=u_f_max)

        ax22.plot(x_range, tau_range, color='orange')
        ax22.fill_between(x_range, tau_range, 0, alpha=0.1, color='orange')
        ax22.set_xlabel(r'$x$ [mm]')
        ax22.set_ylabel(r'$\tau$ [MPa]')
        ax22.set_ylim(ymin=0,ymax=1.5*tau_max)

    def plot_Pw(self, ax):
        w = self.t * self.w_max
        P = 0.001*self.symb.get_Pw_pull(w)
        w_L_b = self.symb.get_w_L_b(w)
        ax.plot(w,P,marker='o', color='blue')
        ax.plot(w_L_b,P,marker='o', color='blue')

        P_range = self.symb.get_Pw_pull(self.w_range)
        w_L_b_range = self.symb.get_w_L_b(self.w_range)
        ax.plot(self.w_range, P_range * 0.001, color='blue', label=r'$w(0)$')
        ax.plot(w_L_b_range, P_range * 0.001, color='blue', linestyle='dashed',
                label=r'$w(L_\mathrm{b})$')
        ax.set_ylabel(r'$P$ [kN]')
        ax.set_xlabel(r'$w$ [mm]')
        ax.legend()

    def subplots(self, fig):
        gs = fig.add_gridspec(1,2, width_ratios=[2., 1.])
        ax1 = fig.add_subplot(gs[0])
        gs2 = gs[1].subgridspec(2, 1)
        ax2 = fig.add_subplot(gs2[0])
        ax22 = ax2.twinx()
        ax3 = fig.add_subplot(gs2[1])
        ax33 = ax3.twinx()
        return ax1, ax2, ax22, ax3, ax33

    def update_plot(self, axes):
        ax, ax2, ax22, ax3, ax33 = axes
        self.plot_Pw(ax)
        self.plot_fields(ax2, ax22, ax3, ax33)