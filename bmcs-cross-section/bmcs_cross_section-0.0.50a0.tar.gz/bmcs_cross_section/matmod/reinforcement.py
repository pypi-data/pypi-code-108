from .matmod import MatMod
import bmcs_utils.api as bu
import sympy as sp
import numpy as np
import traits.api as tr

class ReinfMatMod(MatMod):

    factor = bu.Float(1, MAT=True) # 1. / 1.15
    '''Factor to embed a EC2 based safety factors.
    This multiplication qualitatively modifies the material
    behavior which is not correct. No distinction between
    the scatter of strength and stiffness parameters.
    '''

class SteelReinfMatModSymbExpr(bu.SymbExpr):
    """Piecewise linear concrete material law
    """
    eps = sp.Symbol('eps', real=True)

    eps_sy, eps_ud, E_s = sp.symbols(r'varepsilon_sy, varepsilon_ud, E_s', real=True, nonnegative=True)

    # sig = sp.Piecewise(
    #     (0, eps < -eps_ud),
    #     (-E_s * eps_sy, eps < -eps_sy),
    #     (E_s * eps, eps < eps_sy),
    #     (E_s * eps_sy, eps < eps_ud),
    #     (0, True),
    # )

    ext = 0.7 # extension percentage after failure to avoid numerical solution instability
    sig = sp.Piecewise(
        (0, eps < -eps_ud - ext * eps_sy),
        (-(E_s / ext) * (eps_ud + ext * eps_sy + eps), eps < -eps_ud),
        (-E_s * eps_sy, eps < -eps_sy),
        (E_s * eps, eps < eps_sy),
        (E_s * eps_sy, eps < eps_ud),
        ((E_s / ext) * (eps_ud + ext * eps_sy - eps), eps < eps_ud + ext * eps_sy),
        (0, True),
    )

    symb_model_params = ('E_s', 'eps_sy', 'eps_ud')

    symb_expressions = [
        ('sig', ('eps',)),
    ]


class SteelReinfMatMod(ReinfMatMod, bu.InjectSymbExpr):
    name = 'Steel'

    symb_class = SteelReinfMatModSymbExpr

    E_s = bu.Float(200000, MAT=True, desc='E modulus of steel')
    f_sy = bu.Float(500, MAT=True, desc='steel yield stress')
    eps_ud = bu.Float(0.025, MAT=True, desc='steel failure strain')

    eps_sy = tr.Property(bu.Float, depends_on='+MAT')
    @tr.cached_property
    def _get_eps_sy(self):
        return self.f_sy / self.E_s

    ipw_view = bu.View(
        bu.Item('factor'),
        bu.Item('E_s', latex=r'E_\mathrm{s} \mathrm{[N/mm^{2}]}'),
        bu.Item('f_sy', latex=r'f_\mathrm{sy} \mathrm{[N/mm^{2}]}'),
        bu.Item('eps_ud', latex=r'\varepsilon_\mathrm{ud} \mathrm{[-]}'),
        bu.Item('eps_sy', latex=r'\varepsilon_\mathrm{sy} \mathrm{[-]}', readonly=True),
    )

    def get_eps_plot_range(self):
        return np.linspace(- 1.1*self.eps_ud, 1.1*self.eps_ud, 300)

    def get_sig(self, eps):
        temp = self.f_sy
        self.f_sy *= self.factor
        sig = self.symb.get_sig(eps)
        self.f_sy = temp
        return sig

class CarbonReinfMatModSymbExpr(bu.SymbExpr):
    """Piecewise linear concrete material law
    """
    eps = sp.Symbol('eps', real=True)

    f_t, E = sp.symbols('f_t, E', real=True, nonnegative=True)

    sig = sp.Piecewise(
        (0, eps < 0),
        (E * eps, eps < f_t/E),
        (f_t - E * (eps - f_t/E), eps < 2 * f_t/E),
        (0, True)
    )

    symb_model_params = ('E', 'f_t')

    symb_expressions = [
        ('sig', ('eps',)),
    ]


class CarbonReinfMatMod(ReinfMatMod, bu.InjectSymbExpr):

    name = 'Carbon'

    symb_class = CarbonReinfMatModSymbExpr

    E = bu.Float(200000, MAT=True, desc='E modulus of carbon')
    f_t = bu.Float(2000, MAT=True, desc='carbon breaking stress')

    eps_cr = tr.Property(bu.Float, depends_on='+MAT')
    @tr.cached_property
    def _get_eps_cr(self):
        return self.f_t / self.E

    ipw_view = bu.View(
        bu.Item('factor'),
        bu.Item('E', latex=r'E \mathrm{[N/mm^{2}]}'),
        bu.Item('f_t', latex=r'f_\mathrm{t} \mathrm{[N/mm^{2}]}'),
        bu.Item('eps_cr', latex=r'\varepsilon_\mathrm{cr} \mathrm{[-]}'),
    )

    def get_eps_plot_range(self):
        return np.linspace(- 0.1*self.eps_cr, 1.1*self.eps_cr,300)

    def get_sig(self, eps):
        # TODO: factor should be applied only to strength in case of steel/carbon according to EC2
        temp = self.f_t
        self.f_t *= self.factor
        sig = self.symb.get_sig(eps)
        self.f_t = temp
        return sig
