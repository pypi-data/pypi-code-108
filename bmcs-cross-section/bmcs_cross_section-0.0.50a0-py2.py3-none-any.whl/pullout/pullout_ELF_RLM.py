
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

    #-------------------------------------------------------------------------
    # Declaration of the lambdified methods
    #-------------------------------------------------------------------------

    symb_model_params = ['E_f', 'A_f', 'tau', 'p', 'L_b']

    # List of expressions for which the methods `get_`
    symb_expressions = [
        ('eps_f_x', ('x','P',)),
        ('sig_f_x', ('x','P',)),
        ('u_f_x', ('x','P',)),
        ('w_L_b', ('w',)),
        ('aw_pull', ('w',)),
        ('Pw_pull', ('w',)),
    ]

class PO_ELF_RLM(bu.Model, bu.InjectSymbExpr):
    """
    Pullout elastic long fiber and rigid long matrix
    """
    symb_class = PO_ELF_RLM_Symb

    name = "PO-ELF-RLM"

    E_f = bu.Float(210000, MAT=True)
    tau = bu.Float(8, MAT=True)
    A_f = bu.Float(100, CS=True)
    p = bu.Float(20, CS=True)
    L_b = bu.Float(300, GEO=True)
    w_max = bu.Float(3, BC=True)

    ipw_view = bu.View(
        bu.Item('E_f', latex=r'E_\mathrm{f}~[\mathrm{MPa}]'),
        bu.Item('tau', latex=r'\tau~[\mathrm{MPa}]'),
        bu.Item('A_f', latex=r'A_\mathrm{f}~[\mathrm{mm}^2]'),
        bu.Item('p', latex=r'p~[\mathrm{mm}]'),
        bu.Item('L_b', latex=r'L_\mathrm{b}~[\mathrm{mm}]'),
        bu.Item('w_max', latex=r'w_\max~[\mathrm{mm}]')
    )

    w_range = tr.Property(depends_on='state_changed')
    """Pull-out range w"""
    @tr.cached_property
    def _get_w_range(self):
        return np.linspace(0, self.w_max, 100)

    def update_plot(self, ax):
        P_range = self.symb.get_Pw_pull(self.w_range)
        ax.plot(self.w_range, P_range*0.001)
        ax.set_ylabel(r'$P$ [kN]')
        ax.set_xlabel(r'$w$ [mm]')