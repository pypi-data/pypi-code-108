import traits.api as tr
import numpy as np

from bmcs_utils.api import InteractiveModel, View, Item, Button, ButtonEditor, Float, Int, \
    mpl_align_yaxis_to_zero, mpl_show_one_legend_for_twin_axes, ParametricStudy
from bmcs_utils.api import Model, View, Item, Button, Bool, Float, Int, \
    mpl_align_yaxis, ParametricStudy

from bmcs_beam.beam_config.beam_design import BeamDesign
from bmcs_cross_section.mkappa import MKappa
from scipy.integrate import cumtrapz
import matplotlib.gridspec as gridspec

from bmcs_beam.beam_config.boundary_conditions import BoundaryConditions, BoundaryConfig
from bmcs_beam.beam_config.system.cantilever_system import CantileverDistLoadSystem
from bmcs_beam.beam_config.system.simple_dist_load_system import SimpleDistLoadSystem


class DeflectionProfile(Model):
    '''
    Deflection model of a BMCS beam
    '''

    name = 'Deflection Profile'

    beam_design = tr.Instance(BeamDesign, ())
    mc = tr.Instance(MKappa, ())
    n_load_steps = Int(31)
    w_SLS = Bool(False)

    tree = ['beam_design', 'mc']

    ipw_view = View(
        Item('n_load_steps', latex='n_{\mathrm{load~steps}}'),
        Item('w_SLS', latex='\mathrm{SLS_{limit}}')
    )

    f_exp_data = tr.List
    w_exp_data = tr.List

    plot_F_scale = Float(1, desc='Additional plotting scale that can be added by the user')

    _plot_F_scale = tr.Property()
    def _get__plot_F_scale(self):
        F_scale_to_kN, _ = self.beam_design.system_.get_plot_force_scale_and_unit()
        return self.plot_F_scale * F_scale_to_kN

    F_unit = tr.Property()
    def _get_F_unit(self):
        _, unit = self.beam_design.system_.get_plot_force_scale_and_unit()
        return unit

    def add_fw_exp(self, load_array, deflection_array):
        self.f_exp_data.append(load_array)
        self.w_exp_data.append(deflection_array)

    def get_kappa_x(self):
        '''
        Profile of curvature along the beam
        '''
        M = self.beam_design.get_M_x()
        return self.mc.get_kappa_M(M)
    
    def get_kappa_shrinkage(self):
        '''
        Calculate the shrinkage curvature based on EC2
        '''
        f_ck = 30
        t = 365
        t_s = 3

        alpha_ds1 = 4
        alpha_ds2 = 0.12

        RH = 0.70
        RH_0 = 1.00

        f_cm = 30
        f_cmo = 10
        phi = 2.5
        E_s = 200000
        E_cm = 33000
        S = 1000 * 300 ** 2 / 2
        I = 1000 * 300 ** 3 / 12
        A_c = 1000 * 300
        u = 2 * (1000 + 300)

        eps_ca_infty = 2.5 * (f_ck - 10) * 1e-6
        beta_as_t = 1 - np.exp(- 0.2 * t ** 0.5)
        eps_ca = beta_as_t * eps_ca_infty

        beta_RH = 1.55 * (1 - (RH/RH_0)**3)
        h_0 = 2 * A_c / u
        beta_ds_t_t_s = (t - t_s) / ((t - t_s) + 0.04 * h_0 ** (3/2))
        h_0_ = [100, 200 ,300, 500, 800]
        k_h_ = [ 1, 0.85, 0.75, 0.7, 0.7 ]
        k_h = np.interp(h_0, h_0_, k_h_)
        eps_cd0 = 0.85 * ((220 + 110 * alpha_ds1) * np.exp(-alpha_ds2 * f_cm / f_cmo)) * 1e-6 * beta_RH
        eps_cd = beta_ds_t_t_s * k_h * eps_cd0

        eps_cs = eps_cd + eps_ca

        E_c_eff = E_cm / (1 + phi)
        alpha_e = E_s / E_c_eff
        kappa_cs = eps_cs * alpha_e * S / I

        kappa_cs_ = np.array([kappa_cs])
        kappa_cs_x = np.zeros_like(self.get_kappa_x())
        kappa_cs_x[:] = kappa_cs_

        return kappa_cs_x

    def get_phi_x(self):
        '''
        Calculate the cross sectional rotation by integrating the curvature
        '''
        # TODO rename phi to theta
        kappa_x = self.get_kappa_x() # + 2e-6 #+ self.get_kappa_shrinkage()
        # Kappa = 1/R = d_phi/d_x
        phi_x = cumtrapz(kappa_x, self.beam_design.system_.x, initial=0)

        # resolve the integration constant by requiring zero curvature
        # at the midspan of the beam
        # TODO [SD] this is specific to 3 point bending - generalize
        #           for other loading conditions.
        #           HS: I guess this works for 4pb too (for symmetric beams)

        if not isinstance(self.beam_design.system_, CantileverDistLoadSystem):
                # and not isinstance(self.beam_design.system_, FixedAndRollerDistLoadBeamSystem):
            phi_x -= np.interp(self.beam_design.system_.L / 2, self.beam_design.system_.x, phi_x)
        # elif isinstance(self.beam_design.system_, FixedAndRollerDistLoadBeamSystem):
        #     phi_x -= phi_x[-1]

        # This is a more general approach but not sure from it!
        # kappa_derivative = np.gradient(kappa_x, self.beam_design.system_.x)
        # kappa_derivative_signs = np.sign(kappa_derivative)
        # sign_change = (np.diff(kappa_derivative_signs) != 0) * 1
        # if sign_change.size != 1:
        #     print("Warning: multiple curvature slope changes has been found but only the first is considered!!")
        # sign_change_index = np.where(sign_change == 1)[0][0]
        # phi_x -= phi_x[sign_change_index]

        return phi_x

    def get_w_x(self):
        """
        Profile of deflection along the beam
        """
        phi_x = self.get_phi_x()
        w_x = cumtrapz(phi_x, self.beam_design.system_.x, initial=0)
        # resolve the integration constant by requiring zero deflection
        # at the left support - the right one comes automatically
        # TODO [SR, HS] this is specific to 3 point bending - generalize
        #           for other loading conditions.
        #           HS: I guess this works for 4pb too (for symmetric beams)
        # if self.beam_design.beam_conf_name != BoundaryConfig.FIXED_AND_ROLLER_SUPPORT_DIST_LOAD \
        #         and self.beam_design.beam_conf_name != BoundaryConfig.CANTILEVER_DIST_LOAD:
        #     w_x += w_x[0]
        return w_x

    theta_max = tr.Float(1)

    F_max = tr.Property(Float)
    ''''
    Identify the ultimate limit state based on the maximum moment capacity
    of the cross section.
    '''
    def _get_F_max(self):
        M_I, kappa_I = self.mc.inv_M_kappa
        F_max = self.beam_design.system_.get_max_force(M_I)
        return abs(F_max)

    # def run(self):
    #     F_arr = np.linspace(0, self.F_max, self.n_load_steps)
    #     w_list = []
    #     original_F = self.beam_design.system_.F
    #     for F in F_arr:
    #         if F == 0:
    #             w_list.append(0)
    #         else:
    #             self.beam_design.system_.F = -F
    #             # Append the maximum deflection value that corresponds to the new load (F)
    #             w_list.append(np.fabs(np.min(self.get_w_x())))
    #     self.beam_design.system_.F = original_F
    #     return F_arr, np.array(w_list)
    #
    # def reset(self):
    #     self.theta_F = 0

    F_max_old = Float

    def get_Fw(self):
        F_max = self.F_max
        F_arr = np.linspace(0, F_max, self.n_load_steps)
        w_list = []
        # @todo [SR,RC]: separate the slider theta_F from the calculation
        #                of the datapoints load deflection curve.
        #                use broadcasting in the functions
        #                get_M_x(x[:,np.newaxis], F[np.newaxis,:] and
        #                in get_Q_x, get_kappa_x, get_w_x, get_phi_x, get_w_x
        #                then, the browsing through the history is done within
        #                the two dimensional array of and now loop over theta is
        #                neeeded then. Theta works just as a slider - as originally
        #                introduced.
        original_F = self.beam_design.system_.F
        for F in F_arr:
            if F == 0:
                w_list.append(0)
            else:
                self.beam_design.system_.F = -F
                # Append the maximum deflection value that corresponds to the new load (F)
                w_list.append(np.max(np.fabs(self.get_w_x())))
        if self.F_max_old == F_max:
            self.beam_design.system_.F = original_F
        self.F_max_old = F_max
        return F_arr, np.array(w_list)
    
    # def get_Fw_inx(self, inx):
    #     F_max = self.F_max
    #     F_arr = np.linspace(0, F_max, self.n_load_steps)
    #     w_list = []
    #     # @todo [SR,RC]: separate the slider theta_F from the calculation
    #     #                of the datapoints load deflection curve.
    #     #                use broadcasting in the functions
    #     #                get_M_x(x[:,np.newaxis], F[np.newaxis,:] and
    #     #                in get_Q_x, get_kappa_x, get_w_x, get_phi_x, get_w_x
    #     #                then, the browsing through the history is done within
    #     #                the two dimensional array of and now loop over theta is
    #     #                neeeded then. Theta works just as a slider - as originally
    #     #                introduced.
    #     original_F = self.beam_design.system_.F
    #     for F in F_arr:
    #         if F == 0:
    #             w_list.append(0)
    #         else:
    #             self.beam_design.system_.F = -F
    #             # Append the maximum deflection value that corresponds to the new load (F)
    #             w_list.append(np.fabs(self.get_w_x()[inx]))
    #     if self.F_max_old == F_max:
    #         self.beam_design.system_.F = original_F
    #     self.F_max_old = F_max
    #     return F_arr, np.array(w_list)


    def subplots(self, fig):
        gs = gridspec.GridSpec(1, 2, figure=fig, width_ratios=[0.7, 0.3])

        # ax2, ax3 = fig.subplots(1, 2)
        ax_w = fig.add_subplot(gs[0, 0])
        ax_k = ax_w.twinx()
        ax_Fw = fig.add_subplot(gs[0, 1])
        return ax_w, ax_k, ax_Fw

    def update_plot(self, axes):
        ax_w, ax_k, ax_Fw = axes
        self.plot_fw_with_fmax(ax_Fw)
        self.plot_curvature_along_beam(ax_k)
        self.plot_displacement_along_beam(ax_w)
        mpl_align_yaxis_to_zero(ax_w, ax_k)
        mpl_show_one_legend_for_twin_axes(ax_w, ax_k)

    def plot_fw_with_fmax(self, ax_Fw):
        self.plot_fw(ax_Fw)
        self.plot_exp_fw(ax_Fw)
        current_F = abs(self._plot_F_scale * self.beam_design.system_.F)
        w_SLS = self.beam_design.system_.L / 250
        if self.w_SLS:
            ax_Fw.plot([w_SLS, w_SLS], [0, current_F], color='green')
        ax_Fw.axhline(y=current_F, color='r')
        ax_Fw.annotate('F = ' + str(round(current_F, 2)) + ' ' + self.F_unit, xy=(0, current_F), color='r')

    def plot_exp_fw(self, ax_Fw):
        for w, f in zip(self.w_exp_data, self.f_exp_data):
            ax_Fw.plot(w, f, label='exp deflection', lw=2)

    def plot_curvature_along_beam(self, ax_k):
        x = self.beam_design.system_.x
        kappa_x = self.get_kappa_x()
        # Plotting curvature
        ax_k.plot(x, kappa_x, color='black', label='$\kappa [\mathrm{mm}^{-1}]$')
        # Plotting rotation
        # ax_k.plot(x, self.get_phi_x()/1000, color='green', label='$\phi [rad]$')
        ax_k.fill_between(x, 0, kappa_x, color='gray', alpha=0.1)
        ax_k.invert_yaxis()
        ax_k.set_ylabel(r'$\kappa [\mathrm{mm}^{-1}]$')
        ax_k.set_xlabel(r'$x$')

    def plot_displacement_along_beam(self, ax_w):
        x = self.beam_design.system_.x
        w_x = self.get_w_x()
        ax_w.plot(x, w_x, color='blue', label='$w$ [mm]')
        ax_w.fill_between(x, 0, w_x, color='blue', alpha=0.1)
        ax_w.set_ylabel(r'$w [\mathrm{mm}]$')

    def plot_fw(self, ax_Fw):
        # TODO: expensive calculations for all displacements are running with each plot update to produce new
        #  load-displacement curve, this shouldn't be done for example when only the force has changed
        ax_Fw.set_xlabel(r'$w_\mathrm{max}$ [mm]')
        ax_Fw.set_ylabel(r'$F$ [' + self.F_unit + ']')
        F, w = self.get_Fw()
        ax_Fw.plot(w, self._plot_F_scale * F, label='sim deflection', lw=2)


class LoadDeflectionParamsStudy(ParametricStudy):

    def __init__(self, dp, show_sls_deflection_limit = False):
        self.dp = dp
        self.show_sls_deflection_limit = show_sls_deflection_limit

    def plot(self, ax, title, curve_label):
        ax.set_xlabel(r'$w_\mathrm{max}$ [mm]')
        ax.set_ylabel(r'$F$ [' + self.dp.F_unit + ']')
        F, w = self.dp.get_Fw()

        ax.plot(w, self.dp._plot_F_scale * F, label=curve_label, lw=2)

        if self.show_sls_deflection_limit:
            limit = self.dp.beam_design.system_.L/250
            ax.axvline(x=limit)
            ax.text(limit + 0.1, 0, 'L/250 = ' + str(self.dp.beam_design.system_.L/250), rotation=90)

        ax.set_title(title)
        ax.legend()
