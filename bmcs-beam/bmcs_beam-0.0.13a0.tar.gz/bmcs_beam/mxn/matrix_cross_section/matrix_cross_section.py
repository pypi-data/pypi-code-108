'''
Created on Sep 4, 2012

@todo: introduce the dock feature for the views
@todo: classify the state changes and provide examples.

@author: rch
'''
from traits.api import \
    Float, Property, cached_property, \
    Instance

from .matrix_cross_section_geo import \
    MCSGeo

from .matrix_cross_section_geo_I import \
    MCSGeoI

from .matrix_cross_section_geo_circ import \
    MCSGeoCirc

from .matrix_cross_section_geo_rect import \
    MCSGeoRect

from traitsui.api import \
    View, Item, Group, HGroup, InstanceEditor

from bmcs_beam.mxn.material_types import \
    MTMatrixMixture

from bmcs_beam.mxn.cross_section_component import \
    CrossSectionComponent

import numpy as np

from bmcs_beam.mxn.utils import \
    KeyRef

STATE_AND_GEOMETRY_CHANGE = 'eps_changed,+geo_input,geo.changed'
STATE_LAW_AND_GEOMETRY_CHANGE = 'eps_changed,+geo_input,geo.changed,material_changed,law_changed,material,material_law'

class MatrixCrossSection(CrossSectionComponent):
    '''Cross section characteristics needed for tensile specimens.
    '''
    n_cj = Float(30, auto_set=False, enter_set=True, geo_input=True)
    '''Number of integration points.
    '''

    material = KeyRef('default_mixture', db=MTMatrixMixture.db)

    x = Property(depends_on=STATE_AND_GEOMETRY_CHANGE)
    '''Height of the compressive zone
    '''
    @cached_property
    def _get_x(self):
        height = self.geo.height
        eps_lo = self.state.eps_lo
        eps_up = self.state.eps_up
        if eps_up <= 0 and eps_lo <= 0:
            return height
        elif eps_up == eps_lo:
            return 0.
        else:
            return (abs(eps_up) / (abs(eps_up - eps_lo)) * height)

    z_ti_arr = Property(depends_on=STATE_AND_GEOMETRY_CHANGE)
    '''Discretization of the  compressive zone
    '''
    @cached_property
    def _get_z_ti_arr(self):
        if self.state.eps_up <= 0:  # bending
            zx = min(self.geo.height, self.x)
            return np.linspace(0, zx, self.n_cj)
        elif self.state.eps_lo <= 0:  # bending
            return np.linspace(self.x, self.geo.height, self.n_cj)
        else:  # no compression
            return np.array([0], dtype='f')

    eps_ti_arr = Property(depends_on=STATE_AND_GEOMETRY_CHANGE)
    '''Compressive strain at each integration layer of the compressive zone [-]:
    '''
    @cached_property
    def _get_eps_ti_arr(self):
        # for calibration us measured compressive strain
        # @todo: use mapped traits instead
        #
        height = self.geo.height
        eps_up = self.state.eps_up
        eps_lo = self.state.eps_lo
        eps_j_arr = (eps_up + (eps_lo - eps_up) * self.z_ti_arr /
                     height)
        return (-np.fabs(eps_j_arr) + eps_j_arr) / 2.0

    zz_ti_arr = Property(depends_on=STATE_AND_GEOMETRY_CHANGE)
    '''Distance of discrete slices of compressive zone from the bottom
    '''
    @cached_property
    def _get_zz_ti_arr(self):
        return self.geo.height - self.z_ti_arr

    #===========================================================================
    # Cross section geometry and related parameters
    #===========================================================================

    # Implementation remark:
    # Multiple choice value with memory for values that have already been editted.
    # Once a choice is modified to a previously edited geometric objects,
    # its parameters are still available.
    #
    # @todo: is there a possibility to display self-explaining labels of the
    # choice options (they might be a part of the class implementation)
    # This is a candidate for a separate Trait implementation.
    #
    geo = Instance(MCSGeo)
    '''Geometry of the cross section
    '''
    def _geo_default(self):
        return MCSGeoRect(height=0.06, width=0.2)

    geo_lst = Property()
    @cached_property
    def _get_geo_lst(self):
        lst = [MCSGeoRect(), MCSGeoCirc(), MCSGeoI()]
        for i in range(len(lst)):
            if lst[i].__class__ == self.geo.__class__:
                lst[i] = self.geo
        return lst

    w_ti_arr = Property(depends_on=STATE_AND_GEOMETRY_CHANGE)
    '''Discretization of the  compressive zone - weight factors for general cross section
    '''
    @cached_property
    def _get_w_ti_arr(self):
        return self.geo.width_vct(self.geo.height - self.z_ti_arr)

    #===========================================================================
    # Calculation of compressive stresses and forces
    #===========================================================================

    sig_ti_arr = Property(depends_on=STATE_LAW_AND_GEOMETRY_CHANGE)
    '''Stresses at the j-th integration point.
    '''
    @cached_property
    def _get_sig_ti_arr(self):
        return -self.material_law_.mfn_vct(-self.eps_ti_arr)

    f_ti_arr = Property(depends_on=STATE_LAW_AND_GEOMETRY_CHANGE)
    '''Layer force corresponding to the j-th integration point.
    '''
    @cached_property
    def _get_f_ti_arr(self):
        return self.w_ti_arr * self.sig_ti_arr * self.unit_conversion_factor

    N = Property(depends_on=STATE_LAW_AND_GEOMETRY_CHANGE)
    '''Get the resulting normal force.
    '''
    @cached_property
    def _get_N(self):
        return np.trapz(self.f_ti_arr, self.z_ti_arr)

    M = Property(depends_on=STATE_LAW_AND_GEOMETRY_CHANGE)
    '''Get the resulting moment evaluated with respect to the center line
    '''
    @cached_property
    def _get_M(self):
        return np.trapz(self.f_ti_arr * self.z_ti_arr, self.z_ti_arr)

    #===============================================================================
    # Plotting functions
    #===============================================================================

    def plot_eps(self, ax):
        h = self.geo.height

        # eps ti
        ec = np.hstack([self.eps_ti_arr] + [0, 0])
        zz = np.hstack([self.zz_ti_arr] + [0, h ])
        ax.fill(-ec, zz, color='DodgerBlue')

    def plot_sig(self, ax):
        h = self.geo.height

        # sig ti
        ec = np.hstack([self.sig_ti_arr] + [0, 0])
        zz = np.hstack([self.zz_ti_arr] + [0, h ])
        ax.fill(-ec, zz, color='DodgerBlue')

    def plot(self, fig):
        '''Plots the geometry + concrete law
        '''
        ax1 = fig.add_subplot(1, 2, 1)
        self.geo.plot_geometry(ax1)
        ax2 = fig.add_subplot(1, 2, 2)
        self.material_law_.plot_ax(ax2)

    #===========================================================================
    # Auxiliary methods for tree editor
    #===========================================================================
    node_name = 'Matrix cross section'

    tree_view = View(HGroup(
                Group(
                      Item('n_cj'),
                      Item('material'),
                      Item('material_law'),
                      Group(
                      Item('geo', show_label=False,
                           editor=InstanceEditor(name='geo_lst',
                           editable=True), style='custom'),
                      label='Geometry'
                      ),
                      label='Matrix',
                      springy=True
                      ),
                springy=True,
                ),
                width=0.4,
                height=0.4,
                resizable=True,
                buttons=['OK', 'Cancel'])

if __name__ == '__main__':
    mcs = MatrixCrossSection()
    mcs.configure_traits()
