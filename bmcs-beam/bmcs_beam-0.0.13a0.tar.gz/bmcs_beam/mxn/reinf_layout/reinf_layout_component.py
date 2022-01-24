'''
Created on Sep 4, 2012

@author: rch
'''

from traits.api import \
    WeakRef

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection

from bmcs_beam.mxn.cross_section_component import \
    CrossSectionComponent

STATE_AND_GEOMETRY_CHANGE = 'eps_changed,+geo_input,matrix_cs.geo.changed'
STATE_LAW_AND_GEOMETRY_CHANGE = 'eps_changed,+geo_input,matrix_cs.geo.changed,material_changed,law_changed,material,material_law'

class ReinfLayoutComponent(CrossSectionComponent):
    '''Cross section characteristics needed for tensile specimens
    '''

    matrix_cs = WeakRef(MatrixCrossSection, transient=True)

    def __getstate__ (self):
        '''Overriding __getstate__ because of WeakRef usage
        '''
        state = super(ReinfLayoutComponent, self).__getstate__()

        for key in ['matrix_cs', 'matrix_cs_']:
            if key in state:
                del state[ key ]

        return state

    #===============================================================================
    # Plotting functions
    #===============================================================================

    def plot_geometry(self, ax, clr):
        '''Plot geometry'''
        return

    def plot_eps(self, ax):
        return

    def plot_sig(self, ax):
        return

    def plot(self, fig):
        '''Plots the cross section - particular reinforcement component
        plotted with distinctive color to others
        '''
        ax1 = fig.add_subplot(1, 2, 1)
        self.state.plot_geometry(ax1)
        self.plot_geometry(ax1, clr='red')
        ax2 = fig.add_subplot(1, 2, 2)
        self.material_law_.plot_ax(ax2)
