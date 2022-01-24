
from bmcs_cross_section.cs_design import CSDesign
from bmcs_cross_section.cs_design import Rectangle, ICrossSectionShape
from bmcs_utils.api import InteractiveModel, Item, View, Float
import traits.api as tr
import numpy as np


class BeamDesign(CSDesign):

    name = 'BeamDesign'

    L = Float(5000)

    ipw_view = View(
        Item('L', latex='L \mathrm{[mm]}')
    )

    def subplots(self, fig):
        return fig.subplots(1, 1)

    def update_plot(self, ax):
        beam_points_x_coords = [0, self.L, self.L, 0, 0]
        beam_points_y_coords = [0, 0, self.H, self.H, 0]
        ax.fill(beam_points_x_coords, beam_points_y_coords, color='gray')
        ax.plot(beam_points_x_coords, beam_points_y_coords, color='black')
        ax.annotate('L = {} mm'.format(np.round(self.L), 0), xy=(self.L / 2, self.H * 1.1), color='black')
        ax.axis('equal')
