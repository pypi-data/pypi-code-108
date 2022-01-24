import numpy as np
import traits.api as tr
from anastruct import SystemElements
from bmcs_beam.beam_config.system.system import System
from bmcs_utils.api import Int, Item, View, Float, FloatEditor, IntEditor


class BeamSystem(System):

    name = 'BeamSystem'

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.update_struct()

    L = Float(6000, SYSTEM=True)
    n_x = Int(10, desc='Number of FE elements along the beam.', SYSTEM=True)
    struct = SystemElements()
    _n_x_min = 5

    tree = []

    ipw_view = View(
        Item('L', latex='L \mathrm{[mm]}', editor=FloatEditor(min=10)),
        # Item('n_x', latex='n_x', editor=IntEditor(min_name='_n_x_min')),
        *System.ipw_view.content,
    )

    x = tr.Property(depends_on='L, n_x, n_per_element')
    @tr.cached_property
    def _get_x(self):
        return np.linspace(0, self.L, self.n_x * self.n_per_element)

    def _get_L(self):
        return (self.struct.element_map[self.n_x].vertex_2.x - self.struct.element_map[1].vertex_1.x)

    def subplots(self, fig):
        axes = fig.subplots(3, 1)
        return axes

    def update_plot(self, axes):
        self.plot_struct(axes[0])
        self.plot_bending_moment(axes[1])
        self.plot_shear(axes[2])

    def plot_struct(self, ax):
        ax.get_yaxis().set_visible(False)
        self.struct.plotter.plot_structure(figsize=(8, 2), verbosity=1, loads=True, ax=ax)
        ax.set_xlabel('x [mm]')

    def plot_shear(self, ax):
        # factor=1 is mandatory, here factor=1/1000 is applied [N->kN]
        self.struct.plotter.shear_force(figsize=(8, 2), factor=1/1000, adjust_ax_height=False,
                                           verbosity=1, ax=ax, show=False)
        ax.set_ylabel('Q [kN]')

    def plot_bending_moment(self, ax):
        # Note: factor with (-1) was used to show moment according to our convention
        # factor=1 is mandatory, here factor=1/1e6 is applied [Nmm->kNm]
        self.struct.plotter.bending_moment(figsize=(8, 2), factor=-1/1e6, adjust_ax_height=False,
                                           verbosity=1, ax=ax, show=False)
        ax.set_ylabel('M [kNm]')
        ax.invert_yaxis()
        # M_x = np.array(self.struct.get_element_result_range(unit = "moment")) / M_scale

    # def get_moment(self, n=100):
    #     m = np.array([dict['M'] for dict in self.struct.get_element_results(verbose=True)]).flatten()
    #     x = np.linspace(0, self.L, m.size)
    #     return np.interp(np.linspace(0, self.L, n), x, m)

    def get_moment(self):
        # Note: factor=-1 was used to get the moment sign according to our convention
        return - np.array([dict['M'] for dict in self.struct.get_element_results(verbose=True)]).flatten()

    def get_shear(self):
        return np.array([dict['Q'] for dict in self.struct.get_element_results(verbose=True)]).flatten()

    def get_max_force(self, M_I):
        """ Where M_I the array of moment values corresponding to the studies curvature range [kappa_min, kappa_max] """
        return NotImplementedError
        # elif self.beam_design.beam_conf_name == BoundaryConfig.THREE_SPAN_DIST_LOAD:
        #     # maximum negative moment M_I[0]
        #     F_max = 10 * M_I[0] / self.beam_design.L**2  # max moment is in the 2nd support
        # elif self.beam_design.beam_conf_name == BoundaryConfig.FIXED_SUPPORT_DIST_LOAD:
        #     F_max = 24 * M_I[-1] / self.beam_design.L**2 # max moment is in the span middle
        # elif self.beam_design.beam_conf_name == BoundaryConfig.FIXED_AND_ROLLER_SUPPORT_DIST_LOAD:
        #     # maximum negative moment M_I[0]
        #     F_max = 8 * M_I[0] / self.beam_design.L**2 # max moment is in fixed support

    def get_plot_force_scale_and_unit(self):
        """ Scale which should be applied on the force when plotting """
        return NotImplementedError