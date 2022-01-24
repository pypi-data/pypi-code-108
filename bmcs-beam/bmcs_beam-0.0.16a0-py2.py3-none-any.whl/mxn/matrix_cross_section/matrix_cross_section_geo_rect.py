'''
Created on 25. 2. 2014

@author: Vancikv
'''

from traits.api import \
    Float, Property, cached_property

from traitsui.api import \
    View, Item, Group, HGroup

from .matrix_cross_section_geo import MCSGeo

import numpy as np


class MCSGeoRect(MCSGeo):

    '''Rectangular cross section
    '''
    height = Float(0.3, auto_set=False, enter_set=True, geo_input=True)
    '''total height of cross section
    '''

    width = Float(0.2, auto_set=False, enter_set=True, geo_input=True)
    '''total width of cross section
    '''

    gravity_centre = Property(depends_on='+geo_input')
    '''z distance of gravity centre from upper rim
    '''
    @cached_property
    def _get_gravity_centre(self):
        return self.height / 2

    def get_width(self, z):
        '''returns width of cross section for different vertical coordinates
        '''
        return self.width

    width_vct = Property()

    @cached_property
    def _get_width_vct(self):
        return np.vectorize(self.get_width, otypes=[np.float])

    def plot_geometry(self, ax):
        '''Plot geometry'''
        dx, dz = 0.0, 0.0
        xdata = np.array([0, self.width, self.width, 0, 0], dtype=float)
        zdata = np.array([0, 0, self.height, self.height, 0], dtype=float)
        ax.plot(xdata + dx, zdata + dz, color='blue')
        ax.axis('equal')
        ax.axis([dx - 0.1 * self.width, dx + 1.1 * self.width,
                 dz - 0.1 * self.height, dz + 1.1 * self.height])

    view = View(Item('width'),
                Item('height'),
                resizable=True,
                buttons=['OK', 'Cancel'])

if __name__ == '__main__':
    ge = MCSGeoRect()
    ge.configure_traits()
