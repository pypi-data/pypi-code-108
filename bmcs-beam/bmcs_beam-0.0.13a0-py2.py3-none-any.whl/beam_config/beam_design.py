import traits.api as tr
from bmcs_beam.beam_config.boundary_conditions import BoundaryConditions, BoundaryConfig
from bmcs_cross_section.cs_design import CrossSectionDesign
from bmcs_utils.api import InteractiveModel, \
    Int, Item, View, Float, Range, Button, ButtonEditor, mpl_align_yaxis_to_zero, \
    mpl_show_one_legend_for_twin_axes, FloatRangeEditor
from sympy.physics.continuum_mechanics.beam import Beam
import sympy as sp
import numpy as np
from numbers import Number

class BeamDesign(CrossSectionDesign):

    name = 'Beam Design'

    n_x = Int(100)
    L = Float(5000)
    F = Float(-1000)
    # TODO [HS]: make the conf a dropdown menu when the implementation is done by [RC]
    beam_conf_name = BoundaryConfig.THREE_PB
    beam_conf_name_slider = Range(0.)

    # beam_configs = BoundaryConfig
    # beam_conf = Enum(values='')

    beam = tr.Instance(Beam)

    tree = []

    def _beam_default(self):
        return BoundaryConditions.get_configured_beam(self.L, self.F, self.beam_conf_name)

    x = tr.Property(depends_on='L, n_x')

    @tr.cached_property
    def _get_x(self):
        return np.linspace(0, self.L, self.n_x)

    @tr.observe("beam_conf_name_slider")
    def notify_slider_change(self, event):
        self.beam_conf_name = BoundaryConfig(int(event.new))
        self.beam = BoundaryConditions.get_configured_beam(self.L, self.F, self.beam_conf_name)

    @tr.observe("L")
    def notify_L_change(self, event):
        self.beam = BoundaryConditions.get_configured_beam(event.new, self.F, self.beam_conf_name)

    @tr.observe("F")
    def notify_F_change(self, event):
        self.beam = BoundaryConditions.get_configured_beam(self.L, event.new, self.beam_conf_name)

    # add_force_btn = Button()
    #
    # def _add_force_btn_fired(self):
    #     self.L += 100

    ipw_view = View(
        Item('L', latex='L \mathrm{[mm]}'),
        Item('F', latex='F \mathrm{[N]}'),
        Item('n_x', latex='n_x'),
        Item('beam_conf_name_slider', editor=FloatRangeEditor(label='Beam config', n_steps=5, low=0, high=5)),
        # Item('beam_conf', editor=EnumEditor(label='Beam config', options_tuple_list=beam_configs)),
        # Item('add_force_btn', editor=ButtonEditor(label='Force', icon='plus'))
    )

    def solve_beam_for_reactions(self):
        # TODO: fix this
        #  The following is a quick fix in order for 4pb to work, without it the self.beam is somehow corrupted after
        #  using the function get_Fw() in DeflectionProfile so it's not able to solve the beam for 4pb!
        self.beam = BoundaryConditions.get_configured_beam(self.L, self.F, self.beam_conf_name)

        reactions_names = []

        for load in self.beam.applied_loads:
            load_value = load[0]
            if not isinstance(load_value, Number):
                reactions_names.append(load_value)

        self.beam.solve_for_reaction_loads(*reactions_names)

    def get_M_x(self, solve_beam_first=True):
        if solve_beam_first:
            self.solve_beam_for_reactions()
        x = sp.symbols('x')
        M_ = self.beam.bending_moment().rewrite(sp.Piecewise)
        get_M = sp.lambdify(x, M_, 'numpy')
        return get_M(self.x)

    def get_Q_x(self, solve_beam_first=True):
        if solve_beam_first:
            self.solve_beam_for_reactions()
        x = sp.symbols('x')
        Q_ = self.beam.shear_force().rewrite(sp.Piecewise)
        get_Q = sp.lambdify(x, Q_, 'numpy')
        Q_x = get_Q(self.x)
        return Q_x

    def plot_MQ(self, ax2, ax3):
        x = self.x
        M_scale = 1e+6
        Q_scale = 1000

        M_x = self.get_M_x(solve_beam_first=True) / M_scale
        Q_x = self.get_Q_x(solve_beam_first=False) / Q_scale

        ax2.plot(x, M_x, color='red', label='moment [kNm]')
        ax2.fill_between(x, 0, M_x, color='red', alpha=0.1)
        ax2.set_ylabel('M [kNm]')
        ax2.invert_yaxis()

        ax3.plot(x, Q_x, lw=0.1, color='green', label='shear [kN]')
        ax3.fill_between(x, Q_x, 0, color='green', alpha=0.15)
        ax3.set_ylabel('Q [kN]')
        ax3.set_xlabel('x [mm]')
        ax3.invert_yaxis()
        mpl_show_one_legend_for_twin_axes(ax2, ax3)
        mpl_align_yaxis_to_zero(ax2, ax3)

    def subplots(self, fig):
        ax1, ax2 = fig.subplots(2, 1)
        ax3 = ax2.twinx()
        return ax1, ax2, ax3

    # @todo: [HS] this limits the beam design object to just a MQ profile
    # it is, however meant to be only useful for the deflection calculation.
    # For the shear zone - the interface should be generalized and the
    # beam design should provide more services, namely the access to
    # all the components of the beam, draw the plan from the side view,
    # cross sectional view - indeed the whole design including the supports
    # and loading.
    #
    # An alternative is to declare this package just to a beam_statical_system
    # which is purely 1D and not to call it design. Then a BeamDesign would
    # contain both - beam_bc (a statical system) and cs_design. It would provide
    # functionality to change the parameters of the design - including the
    # length, load configuration and supports (BC in one word).
    #
    def update_plot(self, axes):
        ax1, ax2, ax3 = axes
        BoundaryConditions.plot(ax1, self.beam)
        self.plot_MQ(ax2, ax3)
        ax1.axis('equal')
        ax1.autoscale(tight=True)

    # Quick fix: needed for [bmcs_shear_zone]
    def plot_reinforcement(self, ax):
        L = self.L
        for z in self.cross_section_layout.reinforcement.z_j:
            ax.plot([0,L],[z,z], lw=2, color='brown')