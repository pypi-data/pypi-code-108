import numpy as np
import sympy as sp
import traits.api as tr
from bmcs_cross_section.cs_design import CrossSectionDesign
from scipy.optimize import root
from bmcs_utils.api import \
    InteractiveModel, Instance, Item, View, mpl_align_xaxis, ParametricStudy, \
    SymbExpr, InjectSymbExpr, Float, Int, Bool, FloatRangeEditor, FloatEditor, HistoryEditor

class SolutionNotFoundError(ValueError):
    pass


class MKappaSymbolic(SymbExpr):
    """This class handles all the symbolic calculations
    so that the class MomentCurvature doesn't use sympy ever
    """
    # -------------------------------------------------------------------------
    # Symbolic derivation of expressions
    # -------------------------------------------------------------------------
    kappa = sp.Symbol('kappa', real=True)
    eps_top = sp.symbols('varepsilon_top', real=True)
    eps_bot = sp.symbols('varepsilon_bot', real=True)
    b, h, z = sp.symbols('b, h, z', real=True, nonnegative=True)
    eps = sp.Symbol('varepsilon', real=True)

    # -------------------------------------------------------------------------
    # Symbolic derivation of expressions
    # -------------------------------------------------------------------------
    # Linear profile of strain over the cross section height
    eps_z_ = eps_bot + z * (eps_top - eps_bot) / h
    eps_top_solved = {eps_top: sp.solve(kappa + eps_z_.diff(z), eps_top)[0]}
    eps_z = eps_z_.subs(eps_top_solved)

    # ----------------------------------------------------------------
    # SymbExpr protocol: Parameter names to be fetched from the model
    # ----------------------------------------------------------------
    symb_model_params = ()

    symb_expressions = [
        ('eps_z', ('kappa', 'eps_bot', 'z')),
    ]


class MKappa(InteractiveModel, InjectSymbExpr):
    """Class returning the moment curvature relationship."""
    name = 'Moment-Curvature'

    symb_class = MKappaSymbolic
    cs_design = Instance(CrossSectionDesign, ())

    tree = ['cs_design']
    # Use PrototypedFrom only when the prototyped object is a class
    # (The prototyped attribute behaves similarly
    # to a delegated attribute, until it is explicitly
    # changed; from that point forward, the prototyped attribute
    # changes independently from its prototype.)
    # (it's kind of like tr.DelegatesTo('cs_design.cross_section_shape'))
    cross_section_shape = tr.DelegatesTo('cs_design')
    cross_section_shape_ = tr.DelegatesTo('cs_design')
    cross_section_layout = tr.DelegatesTo('cs_design')
    matrix_ = tr.DelegatesTo('cs_design')

    # Geometry
    H = tr.DelegatesTo('cross_section_shape_')

    DEPSTR = 'state_changed'

    n_m = Int(100, DSC=True, desc='Number of discretization points along the height of the cross-section')

    # @todo: fix the dependency - `H` should be replaced by _GEO
    z_m = tr.Property(depends_on=DEPSTR)

    @tr.cached_property
    def _get_z_m(self):
        return np.linspace(0, self.H, self.n_m)

    low_kappa = Float(0.0, BC=True, GEO=True)
    high_kappa = Float(0.00002, BC=True, GEO=True)
    n_kappa = Int(100, BC=True)
    step_kappa = tr.Property(Float, depends_on='low_kappa, high_kappa')
    @tr.cached_property
    def _get_step_kappa(self):
        return float((self.high_kappa-self.low_kappa)/self.n_kappa)

    kappa_slider = Float(0.0000001)

    ipw_view = View(
        Item('low_kappa', latex=r'\text{Low}~\kappa'), #, editor=FloatEditor(step=0.00001)),
        Item('high_kappa', latex=r'\text{High}~\kappa'), # , editor=FloatEditor(step=0.00001)),
        Item('n_kappa', latex='n_{\kappa}'),
        Item('plot_strain'),
        Item('solve_for_eps_bot_pointwise'),
        Item('n_m', latex='n_m'),
        Item('kappa_slider', latex='\kappa', readonly=True),
             # editor=FloatRangeEditor(low_name='low_kappa',
             #                         high_name='high_kappa',
             #                         n_steps_name='n_kappa')
             # ),
        time_editor=HistoryEditor(var='kappa_slider',
                                  min_var='low_kappa',
                                  max_var='high_kappa',
                                  ),
    )


    idx = tr.Property(depends_on='kappa_slider')

    apply_material_safety_factors = tr.Bool(False)

    @tr.cached_property
    def _get_idx(self):
        ks = self.kappa_slider
        idx = np.argmax(ks <= self.kappa_t)
        return idx

    kappa_t = tr.Property(tr.Array(np.float_), depends_on=DEPSTR)
    '''Curvature values for which the bending moment must be found
    '''

    @tr.cached_property
    def _get_kappa_t(self):
        return np.linspace(self.low_kappa, self.high_kappa, self.n_kappa)

    z_j = tr.Property
    def _get_z_j(self):
        return self.cross_section_layout.z_j

    A_j = tr.Property
    def _get_A_j(self):
        return self.cross_section_layout.A_j

    # Normal force in steel (tension and compression)
    def get_N_s_tj(self, kappa_t, eps_bot_t):
        # get the strain at the height of the reinforcement
        eps_z_tj = self.symb.get_eps_z(
            kappa_t[:, np.newaxis], eps_bot_t[:, np.newaxis],
            self.z_j[np.newaxis, :]
        )
        # Get the crack bridging force in each reinforcement layer
        # given the corresponding crack-bridge law.
        N_s_tj = self.cross_section_layout.get_N_tj(eps_z_tj)
        return N_s_tj

    # TODO - [RC] avoid repeated evaluations of stress profile in
    #            N and M calculations for the same inputs as it
    #            is the case now.
    def get_sig_c_z(self, kappa_t, eps_bot_t, z_tm):
        """Get the stress profile over the height"""
        eps_z = self.symb.get_eps_z(kappa_t[:, np.newaxis], eps_bot_t[:, np.newaxis], z_tm)
        sig_c_z = self.matrix_.get_sig(eps_z)
        return sig_c_z

    # Normal force in concrete (tension and compression)
    def get_N_c_t(self, kappa_t, eps_bot_t):
        z_tm = self.z_m[np.newaxis, :]
        b_z_m = self.cross_section_shape_.get_b(z_tm)
        N_z_tm2 = b_z_m * self.get_sig_c_z(kappa_t, eps_bot_t, z_tm)
        return np.trapz(N_z_tm2, x=z_tm, axis=-1)

    def get_N_t(self, kappa_t, eps_bot_t):
        N_s_t = np.sum(self.get_N_s_tj(kappa_t, eps_bot_t), axis=-1)
        N_c_t = self.get_N_c_t(kappa_t, eps_bot_t)
        return N_c_t + N_s_t

    # SOLVER: Get eps_bot to render zero force

    # num_of_trials = tr.Int(30)

    eps_bot_t = tr.Property(depends_on=DEPSTR)
    r'''Resolve the tensile strain to get zero normal force for the prescribed curvature'''

    # @tr.cached_property
    # def _get_eps_bot_t(self):
    #     initial_step = (self.high_kappa - self.low_kappa) / self.num_of_trials
    #     for i in range(self.num_of_trials):
    #         print('Solution started...')
    #         res = root(lambda eps_bot_t: self.get_N_t(self.kappa_t, eps_bot_t),
    #                    0.0000001 + np.zeros_like(self.kappa_t), tol=1e-6)
    #         if res.success:
    #             print('success high_kappa: ', self.high_kappa)
    #             if i == 0:
    #                 print('Note: high_kappa success from 1st try! selecting a higher value for high_kappa may produce '
    #                       'a more reliable result!')
    #             return res.x
    #         else:
    #             print('failed high_kappa: ', self.high_kappa)
    #             self.high_kappa -= initial_step
    #             self.kappa_t = np.linspace(self.low_kappa, self.high_kappa, self.n_kappa)
    #
    #     print('No solution', res.message)
    #     return res.x

    # @tr.cached_property
    # def _get_eps_bot_t(self):
    #     res = root(lambda eps_bot_t: self.get_N_t(self.kappa_t, eps_bot_t),
    #                0.0000001 + np.zeros_like(self.kappa_t), tol=1e-6)
    #     if not res.success:
    #         raise SolutionNotFoundError('No solution', res.message)
    #     return res.x

    solve_for_eps_bot_pointwise = Bool(True, BC=True, GEO=True)

    @tr.cached_property
    def _get_eps_bot_t(self):
        if self.solve_for_eps_bot_pointwise:
            """ INFO: Instability in eps_bot solutions was caused by unsuitable init_guess value causing a convergence 
            to non-desired solutions. Solving the whole kappa_t array improved the init_guess after each
            calculated value, however, instability still there. The best results were obtained by taking the last 
            solution as the init_guess for the next solution like in the following.. """
            # One by one solution for kappa values
            eps_bot_sol_for_pos_kappa = self._get_eps_bot_piecewise_sol(kappa_pos=True)
            eps_bot_sol_for_neg_kappa = self._get_eps_bot_piecewise_sol(kappa_pos=False)
            res = np.concatenate([eps_bot_sol_for_neg_kappa, eps_bot_sol_for_pos_kappa])
            return res
        else:
            # Array solution for the whole kappa_t
            res = root(lambda eps_bot_t: self.get_N_t(self.kappa_t, eps_bot_t),
                       0.0000001 + np.zeros_like(self.kappa_t), tol=1e-6)
            if not res.success:
                print('No solution', res.message)
            return res.x

    def _get_eps_bot_piecewise_sol(self, kappa_pos=True):
        if kappa_pos:
            kappas = self.kappa_t[np.where(self.kappa_t >= 0)]
        else:
            kappas = self.kappa_t[np.where(self.kappa_t < 0)]

        res = []
        if kappa_pos:
            init_guess = 0.00001
            kappa_loop_list = kappas
        else:
            init_guess = -0.00001
            kappa_loop_list = reversed(kappas)

        for kappa in kappa_loop_list:
            sol = root(lambda eps_bot: self.get_N_t(np.array([kappa]), eps_bot), np.array([init_guess]), tol=1e-6).x[0]

            # This condition is to avoid having init_guess~0 which causes non-convergence
            if abs(sol) > 1e-5:
                init_guess = sol
            res.append(sol)

        if kappa_pos:
            return res
        else:
            return list(reversed(res))

    # POSTPROCESSING
    kappa_cr = tr.Property(depends_on=DEPSTR)
    '''Curvature at which a critical strain is attained at the eps_bot'''

    @tr.cached_property
    def _get_kappa_cr(self):
        res = root(lambda kappa: self.get_N_t(kappa, self.eps_cr),
                   0.0000001 + np.zeros_like(self.eps_cr), tol=1e-10)
        if not res.success:
            print('No kappa_cr solution (for plot_norm() function)', res.message)
        return res.x

    M_s_t = tr.Property(depends_on=DEPSTR)
    '''Bending moment (steel)
    '''

    @tr.cached_property
    def _get_M_s_t(self):
        if len(self.z_j) == 0:
            return np.zeros_like(self.kappa_t)

        eps_z_tj = self.symb.get_eps_z(
            self.kappa_t[:, np.newaxis], self.eps_bot_t[:, np.newaxis],
            self.z_j[np.newaxis, :]
        )

        # Get the crack bridging force in each reinforcement layer
        # given the corresponding crack-bridge law.
        N_tj = self.cross_section_layout.get_N_tj(eps_z_tj)
        return -np.einsum('tj,j->t', N_tj, self.z_j)

    M_c_t = tr.Property(depends_on=DEPSTR)
    '''Bending moment (concrete)
    '''

    @tr.cached_property
    def _get_M_c_t(self):
        z_tm = self.z_m[np.newaxis, :]
        b_z_m = self.cross_section_shape_.get_b(z_tm)
        N_z_tm2 = b_z_m * self.get_sig_c_z(self.kappa_t, self.eps_bot_t, z_tm)
        return -np.trapz(N_z_tm2 * z_tm, x=z_tm, axis=-1)

    M_t = tr.Property(depends_on=DEPSTR)
    '''Bending moment
    '''
    @tr.cached_property
    def _get_M_t(self):
        # print('M - k recalculated')
        eta_factor = 1.
        return eta_factor * (self.M_c_t + self.M_s_t)

    # @tr.cached_property
    # def _get_M_t(self):
    #     initial_step = (self.high_kappa - self.low_kappa) / self.num_of_trials
    #     for i in range(self.num_of_trials):
    #         try:
    #             M_t = self.M_c_t + self.M_s_t
    #         except SolutionNotFoundError:
    #             print('failed high_kappa: ', self.high_kappa)
    #             self.high_kappa -= initial_step
    #         else:
    #             # This will run when no exception has been received
    #             print('success high_kappa: ', self.high_kappa)
    #             if i == 0:
    #                 print('Note: high_kappa success from 1st try! selecting a higher value for high_kappa may produce '
    #                       'a more reliable result!')
    #             return M_t
    #     print('No solution has been found!')
    #     return M_t

    N_s_tj = tr.Property(depends_on=DEPSTR)
    '''Normal forces (steel)
    '''

    @tr.cached_property
    def _get_N_s_tj(self):
        return self.get_N_s_tj(self.kappa_t, self.eps_bot_t)

    eps_tm = tr.Property(depends_on=DEPSTR)
    '''strain profiles
    '''

    @tr.cached_property
    def _get_eps_tm(self):
        return self.symb.get_eps_z(self.kappa_t[:, np.newaxis],
                              self.eps_bot_t[:, np.newaxis], self.z_m[np.newaxis, :])

    sig_tm = tr.Property(depends_on=DEPSTR)
    '''strain profiles
    '''

    @tr.cached_property
    def _get_sig_tm(self):
        return self.get_sig_c_z(
            self.kappa_t, self.eps_bot_t, self.z_m[np.newaxis, :]
        )

    M_norm = tr.Property(depends_on=DEPSTR)
    '''
    '''

    @tr.cached_property
    def _get_M_norm(self):
        # Section modulus @TODO optimize W for var b
        W = (self.b * self.H ** 2) / 6
        sig_cr = self.E_ct * self.eps_cr
        return W * sig_cr

    kappa_norm = tr.Property()

    def _get_kappa_norm(self):
        return self.kappa_cr

    inv_M_kappa = tr.Property(depends_on=DEPSTR)
    '''Return the inverted data points
    '''
    @tr.cached_property
    def _get_inv_M_kappa(self):
        try:
            """cut off the descending tails"""
            M_t = self.M_t
            I_max = np.argmax(M_t)
            I_min = np.argmin(M_t)
            M_I = np.copy(M_t[I_min:I_max + 1])
            kappa_I = np.copy(self.kappa_t[I_min:I_max + 1])
            # find the index corresponding to zero kappa
            idx = np.argmax(0 <= kappa_I)
            # and modify the values such that the
            # Values of moment are non-descending
            M_plus = M_I[idx:]
            M_diff = M_plus[:, np.newaxis] - M_plus[np.newaxis, :]
            n_ij = len(M_plus)
            ij = np.mgrid[0:n_ij:1, 0:n_ij:1]
            M_diff[np.where(ij[1] >= ij[0])] = 0
            i_x = np.argmin(M_diff, axis=1)
            M_I[idx:] = M_plus[i_x]
            return M_I, kappa_I
        except ValueError:
            print('M inverse has not succeeded, the M-Kappa solution may have failed due to '
                  'a wrong kappa range or not suitable material law!')
            return np.array([0]), np.array([0])


    def get_kappa_M(self, M):
        M_I, kappa_I = self.inv_M_kappa
        return np.interp(M, M_I, kappa_I)

    def plot_norm(self, ax1, ax2):
        idx = self.idx
        ax1.plot(self.kappa_t / self.kappa_norm, self.M_t / self.M_norm)
        ax1.plot(self.kappa_t[idx] / self.kappa_norm, self.M_t[idx] / self.M_norm, marker='o')
        ax2.barh(self.z_j, self.N_s_tj[idx, :], height=2, color='red', align='center')
        # ax2.fill_between(eps_z_arr[idx,:], z_arr, 0, alpha=0.1);
        ax3 = ax2.twiny()
        #  ax3.plot(self.eps_tm[idx, :], self.z_m, color='k', linewidth=0.8)
        ax3.plot(self.sig_tm[idx, :], self.z_m)
        ax3.axvline(0, linewidth=0.8, color='k')
        ax3.fill_betweenx(self.z_m, self.sig_tm[idx, :], 0, alpha=0.1)
        mpl_align_xaxis(ax2, ax3)

    M_scale = Float(1e+6)
    plot_strain = Bool(False)

    def plot(self, ax1, ax2, ax3):
        self.plot_mk_and_stress_profile(ax1, ax2)
        if self.plot_strain:
            self.plot_strain_profile(ax3)
        else:
            self.plot_mk_inv(ax3)

    @staticmethod
    def subplots(fig):
        ax1, ax2, ax3 = fig.subplots(1, 3)
        return ax1, ax2, ax3

    def update_plot(self, axes):
        self.plot(*axes)

    def plot_mk_inv(self, ax3):
        try:
            M, kappa = self.inv_M_kappa
            ax3.plot(M / self.M_scale, kappa)
        except ValueError:
            print('M inverse has not succeeded, the M-Kappa solution may have failed due to a wrong kappa range!')

        ax3.set_xlabel('Moment [kNm]')
        ax3.set_ylabel('Curvature[mm$^{-1}$]')

    def plot_mk_and_stress_profile(self, ax1, ax2):
        self.plot_mk(ax1)
        idx = self.idx
        ax1.plot(self.kappa_t[idx], self.M_t[idx] / self.M_scale, color='orange', marker='o')

        if len(self.z_j):
            ax2.barh(self.z_j, self.N_s_tj[idx, :]/self.A_j, height=4, color='red', align='center')
            ax2.set_ylabel('z [mm]')
            ax2.set_xlabel('$\sigma_r$ [MPa]')

        ax22 = ax2.twiny()
        ax22.set_xlabel('$\sigma_c$ [MPa]')
        ax22.plot(self.sig_tm[idx, :], self.z_m)
        ax22.axvline(0, linewidth=0.8, color='k')
        ax22.fill_betweenx(self.z_m, self.sig_tm[idx, :], 0, alpha=0.1)
        mpl_align_xaxis(ax2, ax22)

    def plot_mk(self, ax1):
        ax1.plot(self.kappa_t, self.M_t / self.M_scale, label='M-K')
        ax1.set_ylabel('Moment [kNm]')
        ax1.set_xlabel('Curvature [mm$^{-1}$]')
        ax1.legend()

    def plot_strain_profile(self, ax):
        ax.set_ylabel('z [mm]')
        ax.set_xlabel(r'$\varepsilon$ [-]')
        ax.plot(self.eps_tm[self.idx, :], self.z_m)
        ax.axvline(0, linewidth=0.8, color='k')
        ax.fill_betweenx(self.z_m, self.eps_tm[self.idx, :], 0, alpha=0.1)

    def get_mk(self):
        return self.M_t / self.M_scale, self.kappa_t


class MKappaParamsStudy(ParametricStudy):
    """TODO - put into a separate python module"""
    def __init__(self, mc):
        self.mc = mc

    def plot(self, ax, param_name, value):
        ax.plot(self.mc.kappa_t, self.mc.M_t / self.mc.M_scale, label=param_name + '=' + str(value), lw=2)
        ax.set_ylabel('Moment [kNm]')
        ax.set_xlabel('Curvature [mm$^{-1}$]')
        ax.set_title(param_name)
        ax.legend()
