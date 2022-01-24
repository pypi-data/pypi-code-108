from bmcs_utils.api import Model, Int, Item, View, Float
from bmcs_beam.beam_config.system.beam_system import BeamSystem
import numpy as np

class CantileverDistLoadSystem(BeamSystem):

    name = 'CantileverDistLoadSystem'

    F = Float(-5, SYSTEM=True)
    n_x = 2

    tree = []

    ipw_view = View(
        *BeamSystem.ipw_view.content,
        Item('F', latex='F \mathrm{[kN/m]}'), # kN/m = N/mm
    )

    def update_struct(self):
        self.struct = self.get_new_struct()
        self.struct.add_multiple_elements([[0, 0], [self.L, 0]], self.n_x)
        self.struct.add_support_fixed(1)
        elements = np.arange(1, self.n_x + 1)
        self.struct.q_load(q=self.F, element_id=elements)
        self.struct.solve()

    def get_max_force(self, M_I):
        # This should be done numerically, but here for efficiency and
        # because this is a known case it's given directly
        return 2 * np.min(M_I) / self.L ** 2

    def get_plot_force_scale_and_unit(self):
        """ Scale which should be applied on the force when plotting """
        return 1, 'kN/m'