import matplotlib.patches as mpatches
import numpy as np
import sympy as sp
import traits.api as tr
from bmcs_beam.beam_design.beam_design import BeamDesign
from bmcs_utils.api import InteractiveModel, Item, View, Float, Int
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from sympy.physics.continuum_mechanics.beam import Beam


class BoundaryConditions(InteractiveModel):

    beam_design = tr.Instance(BeamDesign)

    def _beam_design_default(self):
        return BeamDesign()

    name = 'BoundaryConditions'

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

    # 4 point bending example
    x, E, I, F = sp.symbols('x E I F')
    l = sp.symbols('l', positive=True)
    b4p = Beam(l, E, I)
    R1, R2 = sp.symbols('R1  R2')
    b4p.apply_load(R1, 0, -1)
    b4p.apply_load(R2, l, -1)
    b4p.apply_load(-F, l / 3, -1)
    b4p.apply_load(-F, 2 * l / 3, -1)
    b4p.bc_deflection = [(0, 0), (l, 0)]
    b4p.solve_for_reaction_loads(R1, R2)

    # single moment example
    x, E, I, F = sp.symbols('x E I F')
    l = sp.symbols('l', positive=True)  # the l sign
    bmo = Beam(l, E, I)
    R1, R2 = sp.symbols('R1 R2')
    bmo.apply_load(R1, 0, -1)
    bmo.apply_load(R2, l, -1)
    bmo.apply_load(F, l / 2, -2)
    bmo.bc_deflection = [(0, 0), (l, 0)]
    bmo.solve_for_reaction_loads(R1, R2)

    # distrubuted load simple beam example
    E, I, M, V = sp.symbols('E I M V')
    bdi = Beam(l, E, I)
    E, I, R1, R2 = sp.symbols('E I R1 R2')
    bdi.apply_load(R1, 0, -1)
    bdi.apply_load(R2, l, -1)
    bdi.apply_load(-F, 0, 0)
    bdi.bc_deflection = [(0, 0), (l, 0)]
    bdi.solve_for_reaction_loads(R1, R2)

    # 3 span distributed load example
    x, E, I, F = sp.symbols('x E I F')
    l = sp.symbols('l', positive=True)
    b3s = Beam(l, E, I)
    R1, R2, R3, R4 = sp.symbols('R1 R2 R3 R4')
    b3s.apply_load(R1, 0, -1)
    b3s.apply_load(R2, l / 3, -1)
    b3s.apply_load(R3, 2 * l / 3, -1)
    b3s.apply_load(R4, l, -1)
    b3s.apply_load(-F, 0, 0)
    b3s.bc_deflection = [(0, 0), (l / 3, 0), (2 * l / 3, 0), (l, 0)]
    b3s.solve_for_reaction_loads(R1, R2, R3, R4)

    # fixed support example
    E, I, F = sp.symbols('E I F')
    # l = sp.symbols('l', positive=True)
    bf = Beam(l, E, I)
    R1, R2 = sp.symbols('R1  R2')
    M1, M2 = sp.symbols('M1, M2')
    bf.apply_load(R1, 0, -1)
    bf.apply_load(M1, 0, -2)
    bf.apply_load(R2, l, -1)
    bf.apply_load(M2, l, -2)
    bf.apply_load(-F, l / 2, -1)
    bf.bc_deflection = [(0, 0), (l, 0)]
    bf.bc_slope = [(0, 0), (l, 0)]
    bf.solve_for_reaction_loads(R1, R2, M1, M2)

    # conf_name
    conf_name = b3p  # beam configuration name

    L = tr.DelegatesTo('beam_design')
    H = tr.DelegatesTo('beam_design')

    # L = tr.Int(5000, param=True, latex='L \mathrm{[mm]}', minmax=(1000, 10000))
    # H = tr.Int(200, param=True, latex='H \mathrm{[mm]}', minmax=(10, 500))
    f = Float(1000) #TODO solve the issue of l/L and f/F
    n_sup = Int(2)
    G_adj = Float(0.02)
    F_pos = Int(2500)

    ipw_view = View(
        Item('f', latex='F \mathrm{[N]}', minmax=(1000, 10000)), # the name might be confusing
        Item('n_sup', latex='n_{sup} \mathrm{[-]}', minmax=(2, 10)),  # number of supports
        Item('G_adj', latex='G_{adj} \mathrm{[-]}', minmax=(1e-3, 1e-1)),  # Graphic adjustment factor
        Item('F_pos', latex='F_{pos} \mathrm{[mm]}', minmax=(0, 10000)),  # Force position
    )

    def get_supports_loc(self):

        # reading the position of the boundary conditions
        loc_d_ = []
        loc_s_ = []

        for i in range(0, len(self.conf_name.bc_deflection)):
            loc_d_.append(self.conf_name.bc_deflection[i][0])
        for i in range(0, len(self.conf_name.bc_slope)):
            loc_s_.append(self.conf_name.bc_slope[i][0])

        loc_d = dict(list(enumerate(loc_d_)))  # boundary conditions with confined bending
        loc_d_l_ = sp.lambdify((self.l), loc_d)
        loc_d_l = (loc_d_l_(self.L))

        loc_s = dict(list(enumerate(loc_s_)))  # boundary conditions with confined slope
        loc_s_l_ = sp.lambdify((self.l), loc_s)
        loc_s_l = (loc_s_l_(self.L))

        return loc_d_l, loc_s_l

    def subplots(self, fig):
        return fig.subplots(1, 1)

    def update_plot(self, ax):

        # beam 
        ax.fill([0, self.L, self.L, 0, 0], [0, 0, self.H, self.H, 0], color='gray')
        #         ax.plot([0,self.L,self.L,0,0], [0,0,self.H,self.H,0],color='black')

        # supports
        vertices = []
        codes = []

        for i in range(0, len((self.get_supports_loc()[0]))):

            codes += [Path.MOVETO] + [Path.LINETO] * 2 + [Path.CLOSEPOLY]
            vertices += [(self.get_supports_loc()[0][i] - self.L * (self.G_adj), -self.L * self.G_adj),
                         (self.get_supports_loc()[0][i], 0),
                         (self.get_supports_loc()[0][i] + self.L * (self.G_adj), -self.L * self.G_adj),
                         (self.get_supports_loc()[0][i] - self.L * (self.G_adj), -self.L * self.G_adj)]

            if self.get_supports_loc()[0][i] != 0:
                codes += [Path.MOVETO] + [Path.LINETO] + [Path.CLOSEPOLY]
                vertices += [(self.get_supports_loc()[0][i] + (self.L * self.G_adj), -self.L * self.G_adj * 1.2),
                             (self.get_supports_loc()[0][i] - (self.L * self.G_adj), -self.L * self.G_adj * 1.2),
                             (self.get_supports_loc()[0][i] - (self.L * self.G_adj), -self.L * self.G_adj * 1.2)]

        for i in range(0, len((self.get_supports_loc()[1]))):
            codes += [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]
            vertices += [(self.get_supports_loc()[1][i] - self.L * (self.G_adj), -self.L * self.G_adj * 1.2),
                         (self.get_supports_loc()[1][i] - self.L * (self.G_adj), self.H + self.L * self.G_adj * 1.2),
                         (self.get_supports_loc()[1][i] + self.L * (self.G_adj), self.H + self.L * self.G_adj * 1.2),
                         (self.get_supports_loc()[1][i] + self.L * (self.G_adj), -self.L * self.G_adj * 1.2),
                         (self.get_supports_loc()[1][i] - self.L * (self.G_adj), -self.L * self.G_adj * 1.2)]

        vertices = np.array(vertices, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='black', edgecolor='black')
        ax.add_patch(pathpatch)

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

                        ax.plot([(list(Load_x.values())[0])], [(self.H / 2)],
                                marker=r'$\circlearrowleft$', ms=self.H / 5)

                    else:

                        ax.plot([(list(Load_x.values())[0])], [(self.H / 2)],
                                marker=r'$\circlearrowright$', ms=self.H / 5)

                    ax.annotate('{} KN.mm'.format(np.round(self.f / 1000), 0),
                                xy=(list(Load_x.values())[0], self.H * 1.4), color='blue')

                # point load   
                elif load[i][2] == -1:

                    if load[i][0] == -self.F:

                        y_tail = self.L / 20 + self.H
                        y_head = 0 + self.H
                        dy = y_head + x_head / 10

                        arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),
                                                         color='blue', mutation_scale=self.L / 500)
                        ax.annotate('{} KN'.format(np.round(self.f / 1000), 0),
                                    xy=(x_tail, y_tail), color='black')
                        ax.add_patch(arrow)

                    else:

                        y_tail = 0 + self.H
                        y_head = self.L / 20 + self.H
                        dy = y_head + x_head / 10

                        arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),
                                                         color='blue', mutation_scale=self.L / 500)
                        ax.annotate('{} KN'.format(np.round(self.f / 1000), 0),
                                    xy=(x_head, y_head), color='black')
                        ax.add_patch(arrow)

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
                            ax.add_patch(arrow)

                        ax.annotate('{} KN'.format(np.round(self.f / 1000), 0),
                                    xy=(self.L / 2, y_tail * 1.1), color='black')
                        ax.plot([0, self.L], [y_tail, y_tail], color='blue')

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
                            ax.add_patch(arrow)

                        ax.annotate('{} KN'.format(np.round(self.f / 1000), 0),
                                    xy=(self.L / 2, y_head * 1.1), color='black')
                        ax.plot([0, self.L], [y_head, y_head], color='blue')

        ax.axis('equal')
        ax.autoscale(tight=True)
