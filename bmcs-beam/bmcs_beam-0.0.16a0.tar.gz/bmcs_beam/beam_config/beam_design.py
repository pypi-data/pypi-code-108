from numbers import Number

import traits.api as tr
from bmcs_beam.beam_config.system.cantilever_system import CantileverDistLoadSystem
from bmcs_beam.beam_config.system.four_pb_system import FourPBSystem
from bmcs_beam.beam_config.system.simple_dist_load_system import SimpleDistLoadSystem
from bmcs_beam.beam_config.system.three_pb_system import ThreePBSystem
from bmcs_cross_section.cs_design import CrossSectionDesign
from bmcs_utils.api import Item, View, EitherType, Str, Bool


class BeamDesign(CrossSectionDesign):

    name = 'BeamSystem Design'

    system = EitherType(options=[('3pb', ThreePBSystem),
                                 ('4pb', FourPBSystem),
                                 ('simple_beam_dist_load', SimpleDistLoadSystem),
                                 ('cantilever_dist_load', CantileverDistLoadSystem),
                                 # ('fixed_support_dist_load', CarbonReinfMatMod),
                                 # ('fixed_and_roller_support_dist_load', CarbonReinfMatMod),
                                 # ('three_span_dist_load', CarbonReinfMatMod),
                                 # ('three_pb_fixed_support', CarbonReinfMatMod),
                                 # ('single_moment', CarbonReinfMatMod),
                                 ])

    tree = []
    # L = tr.DelegatesTo('system_')
    # F = tr.DelegatesTo('system_')
    # x = tr.DelegatesTo('system_')

    ipw_view = View(
        Item('system'),
    )

    def get_M_x(self):
        return self.system_.get_moment()

    def get_Q_x(self):
        return self.system_.get_shear()

    def subplots(self, fig):
        return self.system_.subplots(fig)

    # @todo: [HS] this limits the beam design object to just a MQ profile
    # it is, however meant to be only useful for the deflection calculation.
    # For the shear zone - the interface should be generalized and the
    # beam design should provide more services, namely the access to
    # all the components of the beam, draw the plan from the side view,
    # cross sectional view - indeed the whole design including the supports
    # and loading.
    # **[HS]: I would take this second variant**
    # An alternative is to declare this package just to a beam_statical_system
    # which is purely 1D and not to call it design. Then a BeamDesign would
    # contain both - beam_bc (a statical beam) and cs_design. It would provide
    # functionality to change the parameters of the design - including the
    # length, load configuration and supports (BC in one word).
    #
    def update_plot(self, axes):
        print('plot updated!')
        self.system_.update_plot(axes)

    # Quick fix: needed for [bmcs_shear_zone]
    def plot_reinforcement(self, ax):
        L = self.system_.L
        for z in self.cross_section_layout.reinforcement.z_j:
            ax.plot([0,L],[z,z], lw=2, color='brown')