'''
Created on 31. 1. 2014

@author: Vancikv
'''

from traits.api import \
    Float, Property, cached_property, \
    Button

from bmcs_beam.mxn.material_types import \
    MTReinfFabric

from traitsui.api import \
    View, Item, VGroup, Group

from .reinf_layout_component import \
    ReinfLayoutComponent, \
    STATE_LAW_AND_GEOMETRY_CHANGE, \
    STATE_AND_GEOMETRY_CHANGE

import numpy as np

from bmcs_beam.mxn.utils import \
    KeyRef

from .reinf_fabric_handler import \
    FabricHandler

class RLCTexLayer(ReinfLayoutComponent):
    '''single layer of textile reinforcement
    '''
    def __init__(self, *args, **metadata):
        if not metadata.get('material', None):
            metadata['material'] = 'default_fabric'
        super(RLCTexLayer, self).__init__(**metadata)

    z_coord = Float(0.2, auto_set=False, enter_set=True, geo_input=True)
    '''distance of the layer from the bottom'''

    material = KeyRef('default_fabric', db=MTReinfFabric.db, law_input=True)

    def convert_eps_u_2_lo(self, eps_up):
        h = self.matrix_cs.geo.height
        eps_u = self.material_law_.eps_u
        eps_lo = eps_up + (eps_u - eps_up) / (h - self.z_coord) * h
        return eps_lo

    def convert_eps_u_2_up(self, eps_lo):
        h = self.matrix_cs.geo.height
        eps_u = self.material_law_.eps_u
        eps_up = eps_lo + (eps_u - eps_lo) / self.z_coord * h
        return eps_up

    #===========================================================================
    # Discretization conform to the tex layers
    #===========================================================================

    n_rovings = Property(depends_on='material,material_changed,matrix_cs.geo.changed')
    '''Number of rovings in the textile layer
    '''
    @cached_property
    def _get_n_rovings(self):
        return int(self.matrix_cs.geo.get_width(self.z_coord) / self.material_.s_0) - 1

    eps = Property(depends_on=STATE_AND_GEOMETRY_CHANGE)
    '''Strain at the level of the reinforcement layer
    '''
    @cached_property
    def _get_eps(self):
        # ------------------------------------------------------------------------
        # geometric params independent from the value for 'eps_t'
        # ------------------------------------------------------------------------
        height = self.matrix_cs.geo.height
        eps_lo = self.state.eps_lo
        eps_up = self.state.eps_up
        # strain at the height of each reinforcement layer [-]:
        #
        return eps_lo + (eps_up - eps_lo) * self.z_coord / height

    eps_t = Property(depends_on=STATE_AND_GEOMETRY_CHANGE)
    '''Tension strain at the level of the layer of the fabrics
    '''
    @cached_property
    def _get_eps_t(self):
        return (np.fabs(self.eps) + self.eps) / 2.0

    eps_c = Property(depends_on=STATE_AND_GEOMETRY_CHANGE)
    '''Compression strain at the level of the layer.
    '''
    @cached_property
    def _get_eps_c(self):
        return (-np.fabs(self.eps) + self.eps) / 2.0

    sig_t = Property(depends_on=STATE_LAW_AND_GEOMETRY_CHANGE)
    '''Stresses at the i-th fabric layer.
    '''
    @cached_property
    def _get_sig_t(self):
        return self.material_law_.mfn.get_value(self.eps_t)

    f_t = Property(depends_on=STATE_LAW_AND_GEOMETRY_CHANGE)
    '''force at the height of reinforcement layer [kN]:
    '''
    @cached_property
    def _get_f_t(self):
        sig_t = self.sig_t
        n_rovings = self.n_rovings
        A_roving = self.material_.A_roving
        return sig_t * n_rovings * A_roving / self.unit_conversion_factor

    N = Property(depends_on=STATE_LAW_AND_GEOMETRY_CHANGE)
    '''Get the resulting normal force.
    '''
    @cached_property
    def _get_N(self):
        return self.f_t

    M = Property(depends_on=STATE_LAW_AND_GEOMETRY_CHANGE)
    '''Get the resulting moment.
    '''
    @cached_property
    def _get_M(self):
        height = self.matrix_cs.geo.height
        return self.f_t * (height - self.z_coord)

    #===========================================================================
    # UI-related functionality
    #===========================================================================

    node_name = 'Textile layer'

    def plot_geometry(self, ax, clr='DarkOrange'):
        '''Plot geometry'''
        width = self.matrix_cs.geo.get_width(self.z_coord)
        w_max = self.matrix_cs.geo.width
        ax.hlines(self.z_coord, (w_max - width) / 2,
                  (w_max + width) / 2, lw=2, color=clr, linestyle='dashed')

    def plot_eps(self, ax):
        eps_lo = self.state.eps_lo
        eps_up = self.state.eps_up

        # eps t
        ax.hlines([self.z_coord], [0], [-self.eps_t], lw=4, color='DarkOrange')

        # reinforcement layer
        ax.hlines([self.z_coord], [min(0.0, -eps_lo, -eps_up)],
                  [max(0.0, -eps_lo, -eps_up)], lw=1, color='black', linestyle='--')

    def plot_sig(self, ax):
        # sig t
        ax.hlines([self.z_coord], [0], [-self.sig_t], lw=4, color='DarkOrange')

    tree_view = View(VGroup(
                      Group(
                      Item('z_coord'),
                      label='Geometry'
                      ),
                      Group(
                      Item('material'),
                      Item('material_law'),
                      label='Fabric material',
                      ),
                      springy=True,
                      ),
                resizable=True,
                handler=FabricHandler(),
                buttons=['OK', 'Cancel']
                )

if __name__ == '__main__':
    layer = RLCTexLayer()
    layer.fabric = 'default_fabric'
    layer.fabric_.A_roving = 0.5
    print(layer.fabric_.state_link_lst)
    layer.configure_traits()
