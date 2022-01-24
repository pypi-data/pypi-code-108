from bmcs_utils.api import Model, Int, Item, View, Float
from bmcs_beam.beam_config.system.beam_system import BeamSystem
import numpy as np

class ThreePBSystem(BeamSystem):

    name = 'ThreePBSystem'

    F = Float(-1000, SYSTEM=True)
    n_x = 2

    tree = []

    ipw_view = View(
        *BeamSystem.ipw_view.content,
        Item('F', latex='F \mathrm{[N]}'),
    )

    def update_struct(self):
        self.struct = self.get_new_struct()
        n_x_to_F = round(0.5 * self.n_x)
        n_x_remains = self.n_x - n_x_to_F
        if n_x_to_F == 1:
            self.struct.add_element([[0, 0], [self.L / 2, 0]])
        else:
            self.struct.add_multiple_elements([[0, 0], [self.L / 2, 0]], n_x_to_F)
        if n_x_remains == 1:
            self.struct.add_element([[self.L / 2, 0], [self.L, 0]])
        else:
            self.struct.add_multiple_elements([[self.L / 2, 0], [self.L, 0]], n_x_remains)

        self.struct.add_support_hinged(1)
        self.struct.add_support_roll(self.n_x + 1)

        self.struct.point_load(n_x_to_F + 1, Fy=self.F)
        self.struct.solve()

    def get_max_force(self, M_I):
        # This should be done numerically, but here for efficiency and
        # because this is a known case it's given directly
        return 4 * np.max(M_I) / self.L

    def get_plot_force_scale_and_unit(self):
        """ Scale which should be applied on the force when plotting """
        return 1/1000, 'kN'