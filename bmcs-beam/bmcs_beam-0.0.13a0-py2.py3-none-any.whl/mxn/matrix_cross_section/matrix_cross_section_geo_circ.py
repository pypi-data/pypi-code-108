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


class MCSGeoCirc(MCSGeo):

    '''Circular shaped cross section
    '''

    radius = Float(0.3, auto_set=False, enter_set=True, geo_input=True)
    '''radius of cross section
    '''

    height = Property(depends_on='radius')
    '''Height of cross section
    '''
    @cached_property
    def _get_height(self):
        return 2 * self.radius

    width = Property(depends_on='radius')
    '''Width of cross section
    '''
    @cached_property
    def _get_width(self):
        return 2 * self.radius

    gravity_centre = Property(depends_on='+geo_input')
    '''z distance of gravity centre from upper rim
    '''
    @cached_property
    def _get_gravity_centre(self):
        return self.radius

    def get_width(self, z):
        '''returns width of cross section for given vertical coordinate
        '''
        r_dist = z - self.radius
        '''transfer distance from top to distance from center
        '''
        width = 2 * np.sqrt(self.radius ** 2 - r_dist ** 2)
        return width

    width_vct = Property()

    @cached_property
    def _get_width_vct(self):
        return np.vectorize(self.get_width, otypes=[np.float])

    def plot_geometry(self, ax):
        '''Plot geometry'''
        dx, dz = self.radius, self.radius
        fi_outline_arr = np.linspace(0, 2 * np.pi, 60)

        ax.plot(np.cos(fi_outline_arr) * self.radius + dx,
                np.sin(fi_outline_arr) * self.radius + dz, color='blue')
        ax.axis('equal')
        ax.axis([dx - self.radius * 1.1, dx + self.radius * 1.1,
                 dz - self.radius * 1.1, dz + self.radius * 1.1])

    view = View(Item('radius'),
                resizable=True,
                buttons=['OK', 'Cancel'])
