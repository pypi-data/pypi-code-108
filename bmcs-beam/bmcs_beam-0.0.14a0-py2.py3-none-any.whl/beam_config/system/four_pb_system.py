import numpy as np
from bmcs_utils.api import Model, Int, Item, View, Float, FloatEditor, IntEditor
from bmcs_beam.beam_config.system.beam_system import BeamSystem
import traits.api as tr

class FourPBSystem(BeamSystem):

    name = 'FourPBSystem'

    F = Float(-1000, SYSTEM=True)
    L_F = Float(1000, desc='length from support to the force', SYSTEM=True)

    _n_x_min = 3
    n_x = 3

    tree = []

    # @tr.observe('L_F')
    # def check_L_F_max(self, event):
    #     if self.L_F > self.L/2 - 1:
    #         self.L_F = self.L/2 - 1

    ipw_view = View(
        *BeamSystem.ipw_view.content,
        Item('F', latex='F \mathrm{[N]}'),
        Item('L_F', latex='L_F \mathrm{[N]}', editor=FloatEditor(min=4)),
    )

    def update_struct(self):
        self.struct = self.get_new_struct()

        n_x_to_F = max(int((self.L_F / self.L) * self.n_x), 1)
        n_x_between_forces = max(self.n_x - 2 * n_x_to_F, 1)
        if n_x_to_F == 1:
            self.struct.add_element([[0, 0], [self.L_F, 0]])
        else:
            self.struct.add_multiple_elements([[0, 0], [self.L_F, 0]], n_x_to_F)
        if n_x_between_forces == 1:
            self.struct.add_element([[self.L_F, 0], [self.L - self.L_F, 0]])
        else:
            self.struct.add_multiple_elements(location=[[self.L_F, 0], [self.L - self.L_F, 0]], n=n_x_between_forces)
        if n_x_to_F == 1:
            self.struct.add_element([[self.L - self.L_F, 0], [self.L, 0]])
        else:
            self.struct.add_multiple_elements([[self.L - self.L_F, 0], [self.L, 0]], n_x_to_F)

        self.struct.add_support_hinged(1)
        self.struct.add_support_roll(self.n_x + 1)

        self.struct.point_load(n_x_to_F + 1, Fy=self.F)
        self.struct.point_load(n_x_to_F + n_x_between_forces + 1, Fy=self.F)
        self.struct.solve()

    def get_max_force(self, M_I):
        # This should be done numerically, but here for efficiency and
        # because this is a known case it's given directly
        return np.max(M_I) / self.L_F

    def get_plot_force_scale_and_unit(self):
        """ Scale which should be applied on the force when plotting """
        return 1/1000, 'kN'