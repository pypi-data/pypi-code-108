'''
Created on 31. 1. 2014

@author: Vancikv
'''

from traits.api import \
    Float, Property, cached_property

from traitsui.api import \
    View, Item, VGroup, Group

from .reinf_layout_component import \
    ReinfLayoutComponent, \
    STATE_LAW_AND_GEOMETRY_CHANGE, \
    STATE_AND_GEOMETRY_CHANGE

from bmcs_beam.mxn.utils import \
    KeyRef

from bmcs_beam.mxn.material_types import \
    MTReinfBar

class RLCBar(ReinfLayoutComponent):
    '''base class for bar reinforcement
    '''
    def __init__(self, *args, **metadata):
        if not metadata.get('material', None):
            metadata['material'] = 'bar_d10'
        super(RLCBar, self).__init__(**metadata)

    x = Float(0.1, auto_set=False, enter_set=True, geo_input=True)
    z = Float(0.45, auto_set=False, enter_set=True, geo_input=True)
    '''position of the bar with respect to lower left
    corner of reinforced cross section
    '''

    material = KeyRef('bar_d10', db=MTReinfBar.db)

    def convert_eps_u_2_lo(self, eps_up):
        h = self.matrix_cs.geo.height
        eps_u = self.material_law_.eps_u
        eps_lo = eps_up + (eps_u - eps_up) / (h - self.z) * h
        return eps_lo

    def convert_eps_u_2_up(self, eps_lo):
        h = self.matrix_cs.geo.height
        eps_u = self.material_law_.eps_u
        eps_up = eps_lo + (eps_u - eps_lo) / self.z * h
        return eps_up

    eps = Property(depends_on=STATE_AND_GEOMETRY_CHANGE)
    '''Strain of the bar
    '''
    @cached_property
    def _get_eps(self):
        # ------------------------------------------------------------------------
        # geometric params independent from the value for 'eps_t'
        # ------------------------------------------------------------------------
        height = self.matrix_cs.geo.height
        eps_lo = self.state.eps_lo
        eps_up = self.state.eps_up
        # strain at the height of reinforcement bar [-]:
        #
        return eps_lo + (eps_up - eps_lo) * self.z / height

    sig = Property(depends_on=STATE_LAW_AND_GEOMETRY_CHANGE)
    '''Stress of the bar
    '''
    @cached_property
    def _get_sig(self):
        return self.material_law_.mfn.get_value(self.eps)

    f = Property(depends_on=STATE_LAW_AND_GEOMETRY_CHANGE)
    '''force in the bar [kN]:
    '''
    @cached_property
    def _get_f(self):
        sig = self.sig
        A_bar = self.material_.area
        return sig * A_bar * self.unit_conversion_factor

    N = Property(depends_on=STATE_LAW_AND_GEOMETRY_CHANGE)
    '''Get the resulting normal force.
    '''
    @cached_property
    def _get_N(self):
        return self.f

    M = Property(depends_on=STATE_LAW_AND_GEOMETRY_CHANGE)
    '''Get the resulting moment.
    '''
    @cached_property
    def _get_M(self):
        height = self.matrix_cs.geo.height
        return self.f * (height - self.z)

    def plot_geometry(self, ax, clr='DarkOrange'):
        '''Plot geometry'''
        ax.plot(self.x, self.z, 'o', color=clr)

    def plot_eps(self, ax):
        ax.hlines([self.z], [0], [-self.eps], lw=4, color='DarkOrange')

    def plot_sig(self, ax):
        h = self.matrix_cs.geo.height
        ax.hlines([self.z], [0], [-self.sig], lw=4, color='DarkOrange')

    node_name = 'Reinforcement Bar'

    tree_view = View(VGroup(
                       Group(
                       Item('x'),
                       Item('z'),
                       label='Position'
                       ),
                       Group(
                       Item('material', show_label=True),
                       Item('material_law', show_label=True),
                       label='Bar material'
                       ),
                       springy=True
                       ),
                       resizable=True,
                       buttons=['OK', 'Cancel']
                       )

if __name__ == '__main__':
    pass
