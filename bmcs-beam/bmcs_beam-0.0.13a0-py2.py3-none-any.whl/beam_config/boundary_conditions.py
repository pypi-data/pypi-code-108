from numbers import Number

import numpy as np
import sympy as sp
import traits.api as tr
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from sympy.physics.continuum_mechanics.beam import Beam
import matplotlib.patches as mpatches

import enum

# class BoundaryConfigSettings:
#     pass

class BoundaryConfig(enum.Enum):
    # The following should be provided as sub classes with possible settings change and get moment ability
    THREE_PB, FOUR_PB, SIMPLE_BEAM_DIST_LOAD, FIXED_SUPPORT_DIST_LOAD, FIXED_AND_ROLLER_SUPPORT_DIST_LOAD, CANTILEVER_DIST_LOAD, THREE_SPAN_DIST_LOAD, THREE_PB_FIXED_SUPPORT, SINGLE_MOMENT = range(9)

    # TODO [HS] This is not initialized when any of the above enums are created, fix this
    first_load_distance = 0

    # settings = BoundaryConfigSettings()


class BoundaryConditions(tr.HasTraits):
    # loads = tr.List
    # supports = tr.List
    name = 'BoundaryConditions'

    @staticmethod
    def get_configured_beam(L, F, config):
        # input beam should have a numerical length and has E and I as symbols, and have predefined supports
        R1, R2, R3, R4, M1, M2 = sp.symbols('R1, R2, R3, R4, M1, M2')
        E, I = sp.symbols('E, I')
        beam = Beam(L, 1, 1)
        if config == BoundaryConfig.THREE_PB:
            # 3 point bending example
            beam.apply_load(R1, 0, -1)
            beam.apply_load(R2, L, -1)
            beam.apply_load(F, L/2, -1)
            beam.bc_deflection = [(0, 0), (L, 0)]

        elif config == BoundaryConfig.FOUR_PB:
            # 4 point bending example
            load_distance = config.first_load_distance
            if load_distance == 0:
                load_distance = L/3
            beam.apply_load(R1, 0, -1)
            beam.apply_load(R2, L, -1)
            beam.apply_load(F, load_distance, -1)
            beam.apply_load(F, L - load_distance, -1)
            beam.bc_deflection = [(0, 0), (L, 0)]
            
        elif config == BoundaryConfig.SIMPLE_BEAM_DIST_LOAD:
            # distributed load simple beam example
            beam.apply_load(R1, 0, -1)
            beam.apply_load(R2, L, -1)
            beam.apply_load(F, 0, 0)
            beam.bc_deflection = [(0, 0), (L, 0)]

        elif config == BoundaryConfig.THREE_SPAN_DIST_LOAD:
            # 3 span distributed load example
            beam.apply_load(R1, 0, -1)
            beam.apply_load(R2, L / 3, -1)
            beam.apply_load(R3, 2 * L / 3, -1)
            beam.apply_load(R4, L, -1)
            beam.apply_load(F, 0, 0)
            beam.bc_deflection = [(0, 0), (L / 3, 0), (2 * L / 3, 0), (L, 0)]

        elif config == BoundaryConfig.THREE_PB_FIXED_SUPPORT:
            # fixed support example
            beam.apply_load(R1, 0, -1)
            beam.apply_load(M1, 0, -2)
            beam.apply_load(R2, L, -1)
            beam.apply_load(M2, L, -2)
            beam.apply_load(F, L / 2, -1)
            beam.bc_deflection = [(0, 0), (L, 0)]
            beam.bc_slope = [(0, 0), (L, 0)]

        elif config == BoundaryConfig.SINGLE_MOMENT:
            # single moment example
            beam.apply_load(R1, 0, -1)
            beam.apply_load(R2, L, -1)
            beam.apply_load(-F, L / 2, -2)
            beam.bc_deflection = [(0, 0), (L, 0)]

        elif config == BoundaryConfig.FIXED_SUPPORT_DIST_LOAD:
            beam.apply_load(R1, 0, -1)
            beam.apply_load(M1, 0, -2)
            beam.apply_load(R2, L, -1)
            beam.apply_load(M2, L, -2)
            beam.apply_load(F, 0, 0)
            beam.bc_deflection = [(0, 0), (L, 0)]
            beam.bc_slope = [(0, 0), (L, 0)]

        elif config == BoundaryConfig.FIXED_AND_ROLLER_SUPPORT_DIST_LOAD:
            beam.apply_load(R1, 0, -1)
            beam.apply_load(R2, L, -1)
            beam.apply_load(M2, L, -2)
            beam.apply_load(F, 0, 0)
            beam.bc_deflection = [(0, 0), (L, 0)]
            beam.bc_slope = [(L, 0)]

        elif config == BoundaryConfig.CANTILEVER_DIST_LOAD:
            beam.apply_load(R1, 0, -1)
            beam.apply_load(M1, 0, -2)
            beam.apply_load(F, 0, 0)
            beam.bc_deflection = [(0, 0)]
            beam.bc_slope = [(L, 0)]

        return beam

    @staticmethod
    def plot(ax, beam):
        L = float(beam.length)
        # ax.annotate('L = {} mm'.format(np.round(L), 0), xy=(L / 2, 5), color='black')

        # Beam
        ax.plot([0, beam.length], [0, 0], linewidth=0.5, color='black')

        # supports
        vertices = []
        codes = []

        support_width = 0.02 * beam.length
        support_line_distance = 1.3 * support_width

        for i, deflection in enumerate(beam.bc_deflection):
            x_loc, def_value = deflection

            # Makeing sure it's a support (deflection value is 0)
            if def_value == 0:
                # Draw the triangle of the support
                codes += [Path.MOVETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
                vertices += [(x_loc, 0),
                             (x_loc + support_width / 2, -support_width),
                             (x_loc - support_width / 2, -support_width),
                             (x_loc, 0)]

                # Add line below the triangle for other supports
                if i > 0:
                    codes += [Path.MOVETO] + [Path.LINETO] + [Path.CLOSEPOLY]
                    vertices += [(x_loc - support_width / 2, -support_line_distance),
                                 (x_loc + support_width / 2, -support_line_distance),
                                 (x_loc + support_width / 2, -support_line_distance)]

        # for i in range(0, len((self.get_supports_loc()[1]))):
        #     codes += [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY]
        #     vertices += [(self.get_supports_loc()[1][i] - L * (self.G_adj), -L * self.G_adj * 1.2),
        #                  (self.get_supports_loc()[1][i] - L * (self.G_adj), self.H + L * self.G_adj * 1.2),
        #                  (self.get_supports_loc()[1][i] + L * (self.G_adj), self.H + L * self.G_adj * 1.2),
        #                  (self.get_supports_loc()[1][i] + L * (self.G_adj), -L * self.G_adj * 1.2),
        #                  (self.get_supports_loc()[1][i] - L * (self.G_adj), -L * self.G_adj * 1.2)]

        vertices = np.array(vertices, float)
        path = Path(vertices, codes)
        pathpatch = PathPatch(path, facecolor='black', edgecolor='black')
        ax.add_patch(pathpatch)

        # loads
        load = beam.applied_loads
        value = [0]
        pos = [0]
        type = [0]

        # reading the value and the position of external loads
        for load in beam.applied_loads:
            load_value = load[0]
            if isinstance(load_value, Number):
                load_value = float(load[0])
                load_position = float(load[1])
                load_type = float(load[2])

                x_tail = load_position
                x_head = load_position

                # Point load
                if load_type == -1:
                    y_tail = L / 20
                    y_head = 2.
                    xy_annotate = (x_tail, y_tail)

                    if load_value == abs(load_value):
                        y_tail = 2.
                        y_head = L / 20
                        xy_annotate = (x_head, y_head)

                    arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),
                                                     color='blue', mutation_scale=L / 500)
                    ax.annotate('{} kN'.format(-round(load_value / 1000., 2)), xy=xy_annotate, color='black')
                    ax.add_patch(arrow)

        # for i in range(0, len(load)):
        #     if load[i][0] == -self.F or load[i][0] == self.F:
        #         value[0] = (load[i][0])
        #         pos[0] = (load[i][1])
        #         load_dic = dict(zip(value, pos))
        #         load_ = sp.lambdify((self.F, L), load_dic)
        #         Load_x = load_(self.f, L)
        #
        #         # load arrow parameters
        #         x_tail = (list(Load_x.values())[0])
        #         x_head = (list(Load_x.values())[0])
        #
        #         # moment
        #         if load[i][2] == -2:
        #
        #             if load[i][0] == -self.F:
        #
        #                 ax.plot([(list(Load_x.values())[0])], [(self.H / 2)],
        #                         marker=r'$\circlearrowleft$', ms=self.H / 5)
        #
        #             else:
        #
        #                 ax.plot([(list(Load_x.values())[0])], [(self.H / 2)],
        #                         marker=r'$\circlearrowright$', ms=self.H / 5)
        #
        #             ax.annotate('{} KN.mm'.format(np.round(self.f / 1000), 0),
        #                         xy=(list(Load_x.values())[0], self.H * 1.4), color='blue')
        #
        #         # point load
        #         elif load[i][2] == -1:
        #
        #             if load[i][0] == -self.F:
        #
        #                 y_tail = L / 20 + self.H
        #                 y_head = 0 + self.H
        #                 dy = y_head + x_head / 10
        #
        #                 arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),
        #                                                  color='blue', mutation_scale=L / 500)
        #                 ax.annotate('{} KN'.format(np.round(self.f / 1000), 0),
        #                             xy=(x_tail, y_tail), color='black')
        #                 ax.add_patch(arrow)
        #
        #             else:
        #
        #                 y_tail = 0 + self.H
        #                 y_head = L / 20 + self.H
        #                 dy = y_head + x_head / 10
        #
        #                 arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),
        #                                                  color='blue', mutation_scale=L / 500)
        #                 ax.annotate('{} KN'.format(np.round(self.f / 1000), 0),
        #                             xy=(x_head, y_head), color='black')
        #                 ax.add_patch(arrow)
        #
        #         else:
        #
        #             if load[i][0] == -self.F:
        #                 y_tail = L / 20 + self.H
        #                 y_head = 0 + self.H
        #                 dy = y_head + x_head / 10
        #
        #                 # distributed load
        #                 l_step = 0
        #                 while l_step <= L:
        #                     x_tail = (list(Load_x.values())[0]) + l_step
        #                     y_tail = L / 20 + self.H
        #                     x_head = (list(Load_x.values())[0]) + l_step
        #                     y_head = 0 + self.H
        #                     dy = y_head + x_head / 10
        #                     l_step += L / 10
        #                     arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),
        #                                                      color='blue', mutation_scale=L / 500)
        #                     ax.add_patch(arrow)
        #
        #                 ax.annotate('{} KN'.format(np.round(self.f / 1000), 0),
        #                             xy=(L / 2, y_tail * 1.1), color='black')
        #                 ax.plot([0, L], [y_tail, y_tail], color='blue')
        #
        #             else:
        #                 y_tail = 0 + self.H
        #                 y_head = L / 20 + self.H
        #                 dy = y_head + x_head / 10
        #
        #                 # distributed load
        #                 l_step = 0
        #                 while l_step <= L:
        #                     x_tail = (list(Load_x.values())[0]) + l_step
        #                     y_tail = 0 + self.H
        #                     x_head = (list(Load_x.values())[0]) + l_step
        #                     y_head = L / 20 + self.H
        #                     dy = y_head + x_head / 10
        #                     l_step += L / 10
        #                     arrow = mpatches.FancyArrowPatch((x_tail, y_tail), (x_head, y_head),
        #                                                      color='blue', mutation_scale=L / 500)
        #                     ax.add_patch(arrow)
        #
        #                 ax.annotate('{} KN'.format(np.round(self.f / 1000), 0),
        #                             xy=(L / 2, y_head * 1.1), color='black')
        #                 ax.plot([0, L], [y_head, y_head], color='blue')

        ax.axis('equal')
        ax.autoscale(tight=True)


# class BoundaryCondition(tr.HasTraits):
#     x_loc = tr.Float
#
#
# class Support(BoundaryCondition):
#     constrained_directions = tr.Tuple(0, 1)  # free on x and constrained on y
#
#
# class Load(BoundaryCondition):
#     value = tr.Float
