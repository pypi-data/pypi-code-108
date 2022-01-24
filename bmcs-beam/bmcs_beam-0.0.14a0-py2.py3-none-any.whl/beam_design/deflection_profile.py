import matplotlib.patches as mpatches
import numpy as np
import sympy as sp
import traits.api as tr
from bmcs_beam.beam_design.boundary_conditions import BoundaryConditions
from bmcs_beam.moment_curvature.moment_curvature import MomentCurvature
from bmcs_utils.api import InteractiveModel, Item, View, Float, Int
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from scipy.integrate import cumtrapz

from sympy.physics.continuum_mechanics.beam import Beam


class DeflectionProfile(InteractiveModel):
    name = 'DeflectionProfile'

    '''Temporary beam definition'''
    # 3 point bending example

    x, E, I, F = sp.symbols('x E I F')
    l = sp.symbols('l', positive=True)  # the l sign
    b3p = Beam(l, E, I)
    R1, R2 = sp.symbols('R1 R2')
    b3p.apply_load(R1, 0, -1)
    b3p.apply_load(R2, l, -1)
    b3p.apply_load(-F, l / 2, -1)
    b3p.bc_deflection = [(0, 0), (l, 0)]
    b3p.solve_for_reaction_loads(R1, R2)

    conf_name = b3p  # beam configuration name

    mc = MomentCurvature()

    bc = tr.Instance(BoundaryConditions, ())
    supports_loc = tr.Property(depends_on='bc')

    @tr.cached_property
    def _get_supports_loc(self):
        return self.bc.get_supports_loc()

    #     mc = tr.Property(depends_on = '+param')
    #     @tr.cached_property
    #     def _get_mc(self):
    #         mc = MomentCurvature()
    #         return mc

    # Reinforcement
    E_carbon = Int(200000)
    width = Float(10)
    thickness = Float(1)
    spacing = Float(1)
    n_layers = Int(1)
    A_roving = Float(1)

    # Concerte cross section
    L = Int(5000, param=True, latex='L \mathrm{mm}', minmax=(10, 10000))
    H = Int(200, param=True, latex='H \mathrm{mm}', minmax=(10, 500))
    B = Int(10, param=True, latex='B \mathrm{mm}', minmax=(10,500))
    E_con = Int(14000)
    f = Float(5000)
    n_x = Int(100)
    G_adj = Float(0.015)

    ipw_view = View(
        Item('E_con', latex='E \mathrm{MPa}', minmax=(14000, 41000)),
        Item('f', latex='F \mathrm{N}', minmax=(10, 100000)),
        Item('E_carbon', latex='E_r \mathrm{MPa}', minmax=(200000, 300000)),
        Item('width', latex='rov_w \mathrm{mm}', minmax=(10, 450)),
        Item('thickness', latex='rov_t \mathrm{mm}', minmax=(1, 100)),
        Item('spacing', latex='ro_s \mathrm{mm}', minmax=(1, 100)),
        Item('n_layers', latex='n_l \mathrm{-}', minmax=(1, 100)),
        Item('A_roving', latex='A_r \mathrm{mm^2}', minmax=(1, 100)),
        Item('G_adj', latex='G_{adj} \mathrm{-}', minmax=(1e-3, 1e-1)),
        Item('n_x', latex='n_x \mathrm{-}', minmax=(1, 1000))
    )

    x = tr.Property(depends_on='+param')

    @tr.cached_property
    def _get_x(self):
        return np.linspace(0, self.L, self.n_x)

    E_comp = tr.Property(depends_on='+param')

    @tr.cached_property
    def _get_E_comp(self):
        A_composite = self.B * self.H
        n_rovings = self.width / self.spacing
        A_layer = n_rovings * self.A_roving
        A_carbon = self.n_layers * A_layer
        A_concrete = A_composite - A_carbon
        E_comp = (self.E_carbon * A_carbon + self.E_con * A_concrete) / (A_composite)
        return E_comp

    def get_M_x(self):
        x, F, l = sp.symbols('x F l')
        M_ = self.conf_name.bending_moment().rewrite(sp.Piecewise)
        get_M = sp.lambdify((x, F, l), M_, 'numpy')
        M_x = get_M(self.x, self.f, self.L)
        return M_x

    def get_Q_x(self):
        x, F, l = sp.symbols('x F l')
        Q_ = self.conf_name.shear_force().rewrite(sp.Piecewise)
        get_Q = sp.lambdify((x, F, l), Q_, 'numpy')
        Q_x = get_Q(self.x, self.f, self.L)
        return Q_x

    def get_kappa_x(self):
        M = self.get_M_x()
        #         I = (self.B*self.H**3)/12
        return self.mc.get_kappa(M)

    #         return M / I / self.E_comp

    # b3p, b4p & bdi (single span configs)
    def get_phi_x(self):
        kappa_x = self.get_kappa_x()
        phi_x = cumtrapz(kappa_x, self.x, initial=0)
        phi_L2 = np.interp(self.L / 2, self.x, phi_x)
        phi_x -= phi_L2
        return phi_x

    # b3s
    #     def get_phi_x(self):
    #         kappa_x = self.get_kappa_x()
    #         phi_x = cumtrapz(kappa_x, self.x, initial=0)
    #         peaks, _ = find_peaks(M_x, height=0)
    #         M_x_p = M_x[peaks]
    #         phi_L2 = np.interp(self.M_x_p, self.x, phi_x)
    #         phi_x -= phi_L2
    #         return phi_x

    def get_w_x(self):
        phi_x = self.get_phi_x()
        w_x = cumtrapz(phi_x, self.x, initial=0)
        w_x += w_x[0]
        return w_x

    def subplots(self, fig):
        return fig.subplots(3, 1)

    def update_plot(self, axes):
        ax1, ax2, ax3 = axes

        # beam
        ax1.fill([0, self.L, self.L, 0, 0], [0, 0, self.H, self.H, 0], color='gray')
        #         ax.plot([0,self.L,self.L,0,0], [0,0,self.H,self.H,0],color='black')

        # supports
        vertices = []
        codes = []

        for i in range(0, len(self.supports_loc[0])):

            codes += [Path.MOVETO] + [Path.LINETO] * 2 + [Path.CLOSEPOLY]
            vertices += [(self.supports_loc[0][i] - self.L * (self.G_adj), -self.L * self.G_adj),
                         (self.supports_loc[0][i], 0),
                         (self.supports_loc[0][i] + self.L * (self.G_adj), -self.L * self.G_adj),
                         (self.supports_loc[0][i] - self.L * (self.G_adj), -self.L * self.G_adj)]

            if self.supports_loc[0][i] != 0:
                codes += [Path.MOVETO] + [Path.LINETO] + [Path.CLOSEPOLY]
                vertices += [(self.supports_loc[0][i] + (self.L * self.G_adj), -self.L * self.G_adj * 1.2),
                             (self.supports_loc[0][i] - (self.L * self.G_adj), -self.L * self.G_adj * 1.2),
                             (self.supports_loc[0][i] - (self.L * self.G_adj), -self.L * self.G_adj * 1.2)]

        for i in range(0, len((self.supports_loc[1]))):
            codes += [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]
            vertices += [(self.supports_loc[1][i] - self.L * (self.G_adj), -self.L * self.G_adj * 1.2),
                         (self.supports_loc[1][i] - self.L * (self.G_adj), self.H + self.L * self.G_adj * 1.2),
                         (self.supports_loc[1][i] + self.L * (self.G_adj), self.H + self.L * self.G_adj * 1.2),
                         (self.supports_loc[1][i] + self.L * (self.G_adj), -self.L * self.G_adj * 1.2),
                         (self.supports_loc[1][i] - self.L * (self.G_adj), -self.L * self.G_adj * 1.2)]

        vertices = np.array(vertices, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='black', edgecolor='black')
        ax1.add_patch(pathpatch)

        # loads
        load = self.conf_name.applied_loads
        value = [0]
        pos = [0]
        type = [0]

        # reading the value and the positoin of external loads
        for i in range(0, len(load)):
            if load[i][0] == -self.F or load[i][0] == self.F:
                value[0] = (load[i][0])
                pos[0] = (load[i][1])
                load_dic = dict(zip(value, pos))
                load_ = sp.lambdify((self.F, self.l), load_dic)
                Load_x = load_(self.f, self.L)

                # load arrow parameters
                x_tail = (list(Load_x.values())[0])
                x_head = (list(Load_x.values())[0])

                # moment
                if load[i][2] == -2:

                    if load[i][0] == -self.F:

                        ax1.plot([(list(Load_x.values())[0])], [(self.H / 2)],
                                 marker=r'$\circlearrowleft$', ms=self.H / 5)

                    else:

                        ax1.plot([(list(Load_x.values())[0])], [(self.H / 2)],
                                 marker=r'$\circlearrowright$', ms=self.H / 5)

                    ax1.annotate('{} KN.mm'.format(np.round(self.F / 1000), 0),
                                 xy=(list(Load_x.values())[0], self.H * 1.4), color='blue')

                # point load
                elif load[i][2] == -1:

                    if load[i][0] == -self.F:

                        y_tail = self.L / 20 + self.H
                        y_head = 0 + self.H
                        dy = y_head + x_head / 10

                        arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),
                                                         color='blue', mutation_scale=self.L / 500)
                        ax1.annotate('{} KN'.format(np.round(self.f / 1000), 0),
                                     xy=(x_tail, y_tail), color='black')
                        ax1.add_patch(arrow)

                    else:

                        y_tail = 0 + self.H
                        y_head = self.L / 20 + self.H
                        dy = y_head + x_head / 10

                        arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),
                                                         color='blue', mutation_scale=self.L / 500)
                        ax1.annotate('{} KN'.format(np.round(self.f / 1000), 0),
                                     xy=(x_head, y_head), color='black')
                        ax1.add_patch(arrow)

                else:

                    if load[i][0] == -self.F:
                        y_tail = self.L / 20 + self.H
                        y_head = 0 + self.H
                        dy = y_head + x_head / 10

                        # distributed load
                        l_step = 0
                        while l_step <= self.L:
                            x_tail = (list(Load_x.values())[0]) + l_step
                            y_tail = self.L / 20 + self.H
                            x_head = (list(Load_x.values())[0]) + l_step
                            y_head = 0 + self.H
                            dy = y_head + x_head / 10
                            l_step += self.L / 10
                            arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),
                                                             color='blue', mutation_scale=self.L / 500)
                            ax1.add_patch(arrow)

                        ax1.annotate('{} KN'.format(np.round(self.F / 1000), 0),
                                     xy=(self.L / 2, y_tail * 1.1), color='black')
                        ax1.plot([0, self.L], [y_tail, y_tail], color='blue')

                    else:
                        y_tail = 0 + self.H
                        y_head = self.L / 20 + self.H
                        dy = y_head + x_head / 10

                        # distributed load
                        l_step = 0
                        while l_step <= self.L:
                            x_tail = (list(Load_x.values())[0]) + l_step
                            y_tail = 0 + self.H
                            x_head = (list(Load_x.values())[0]) + l_step
                            y_head = self.L / 20 + self.H
                            dy = y_head + x_head / 10
                            l_step += self.L / 10
                            arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),
                                                             color='blue', mutation_scale=self.L / 500)
                            ax1.add_patch(arrow)

                        ax1.annotate('{} KN'.format(np.round(self.f / 1000), 0),
                                     xy=(self.L / 2, y_head * 1.1), color='black')
                        ax1.plot([0, self.L], [y_head, y_head], color='blue')


        x = self.x

        #         M_x = self.get_M_x()
        #         ax2.plot(x, -M_x, color='red', label='moment [N.mm]')
        #         leg = ax2.legend();

        #         Q_x = self.get_Q_x()
        #         ax3.plot(x, Q_x, color='green', label='shear [N]')
        #         leg = ax3.legend();

        kappa_x = self.get_kappa_x()    #self.mc.get_kappa(M)
        ax2.plot(x, kappa_x, color='black', label='$kappa$ [-]')
        ax2.legend();

        #         phi_x = self.get_phi_x()
        #         ax4.plot(x, phi_x, color='green', label='phi [-]')
        #         leg = ax4.legend();

        w_x = self.get_w_x()
        ax3.plot(x, w_x, color='blue', label='$w$ [mm]')
        ax3.legend();