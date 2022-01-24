'''
Created on 25. 2. 2014

@author: Vancikv
'''

from traits.api import \
    Float, Property, cached_property

from traitsui.api import \
    View, Item, Group

from .matrix_cross_section_geo import MCSGeo

import numpy as np


class MCSGeoI(MCSGeo):

    '''I-shaped cross section
    '''

    height = Float(0.6, auto_set=False, enter_set=True, geo_input=True)
    '''total height of crosssection
    '''

    height_up = Float(0.1, auto_set=False, enter_set=True, geo_input=True)
    '''height of upper flange
    '''

    height_lo = Float(0.1, auto_set=False, enter_set=True, geo_input=True)
    '''height of lower flange
    '''

    width_up = Float(0.4, auto_set=False, enter_set=True, geo_input=True)
    '''width of upper flange
    '''

    width_lo = Float(0.6, auto_set=False, enter_set=True, geo_input=True)
    '''width of lower flange
    '''

    width_st = Float(0.2, auto_set=False, enter_set=True, geo_input=True)
    '''width of stalk
    '''

    width = Property(depends_on='+geo_input')
    '''Width of cross section
    '''
    @cached_property
    def _get_width(self):
        return max(self.width_lo, self.width_up)

    gravity_centre = Property(depends_on='+geo_input')
    '''z distance of gravity centre from upper rim
    '''
    @cached_property
    def _get_gravity_centre(self):
        A_up, z_up = self.width_up * self.height_up, self.height_up / 2
        A_lo, z_lo = self.width_lo * \
            self.height_lo, self.height - self.height_lo / 2
        A_st, z_st = self.width_st * \
            (self.height - self.height_up - self.height_lo), (self.height +
                                                              self.height_up - self.height_lo) / 2
        return (A_up * z_up + A_lo * z_lo + A_st * z_st) / (A_up + A_lo + A_st)

    def get_width(self, z):
        '''Returns width of cross section for different vertical coordinates
        '''
        width = self.width_lo + (np.sign(z - self.height_lo) + 1) / 2 * (self.width_st - self.width_lo) + \
            (np.sign(z - self.height + self.height_up) + 1) / \
            2 * (self.width_up - self.width_st)
        return width

    width_vct = Property()

    @cached_property
    def _get_width_vct(self):
        return np.vectorize(self.get_width, otypes=[np.float])

    def plot_geometry(self, ax):
        '''Plot geometry'''
        w_max = self.width

        dx, dz = 0.0, 0.0

        xdata = np.array([-self.width_lo / 2, self.width_lo / 2, self.width_lo / 2, self.width_st / 2,
                          self.width_st / 2, self.width_up /
                          2, self.width_up / 2, -self.width_up / 2,
                          - self.width_up / 2, -self.width_st /
                          2, -self.width_st / 2,
                          - self.width_lo / 2, -self.width_lo / 2], dtype=float) + w_max / 2

        zdata = np.array([0, 0, self.height_lo, self.height_lo, self.height - self.height_up,
                          self.height - self.height_up, self.height, self.height, self.height -
                          self.height_up,
                          self.height - self.height_up, self.height_lo, self.height_lo, 0], dtype=float)

        ax.plot(xdata + dx, zdata + dz, color='blue')

        ax.axis('equal')
        ax.axis([dx - 0.1 * w_max, dx + 1.1 * w_max,
                 dz - 0.1 * self.height, dz + 1.1 * self.height])

    view = View(Item('width_up'),
                Item('width_lo'),
                Item('width_st'),
                Item('height'),
                Item('height_lo'),
                Item('height_up'),
                resizable=True,
                buttons=['OK', 'Cancel'])
