'''
Created on Sep 4, 2012

@author: rch
'''
from traits.api import \
    Int, Instance, Property, List, \
    cached_property, Event, on_trait_change

from traitsui.api import \
    View, Item, Group, HGroup, RangeEditor

from bmcs_beam.mxn.mxn_tree_node import \
    MxNTreeNode

from bmcs_beam.mxn.cross_section import \
    CrossSection

from bmcs_beam.mxn.reinf_layout import \
    RLCTexUniform

import numpy as np

from bmcs_beam.mxn.matrix_cross_section import \
    MatrixCrossSection, MCSGeoRect

class MxNDiagram(MxNTreeNode):

    modified = Event
    def set_modified(self):
        self.modified = True

    tree_node_list = List(Instance(CrossSection))
    def _tree_node_list_default(self):
        return [CrossSection(notify_change_ext=self.set_modified,
                            reinf=[RLCTexUniform(
                                      n_layers=12,
                                      material='default_fabric')],
                            matrix_cs=MatrixCrossSection(geo=MCSGeoRect(
                                      width=0.2, height=0.06), n_cj=20,
                                      material='default_mixture',
                                      material_law='constant'))]

    @on_trait_change('tree_node_list')
    def cs_changed(self):
        self.modified = True

    cs = Property(depends_on='tree_node_list')
    def _get_cs(self):
        val = self.tree_node_list[0]
        val.notify_change_ext = self.set_modified
        return val
    def _set_cs(self, val):
        self.tree_node_list = [val]

    eps_cu = Property()
    def _get_eps_cu(self):
        return -self.cs.matrix_cs_with_state.material_law_.eps_c_u

    strain_env_reinf = Property()
    '''Contains the reinforcement element that determines the strain envelope.
    '''
    def _get_strain_env_reinf(self):
        eps_lo_arr = np.array([[r, r.convert_eps_u_2_lo(eps_up=self.eps_cu)]
                               for r in self.cs.reinf_components_with_state])
        try:
            min_index = np.argmin(eps_lo_arr[:, 1])
        except:
            # Returns None in case there is no reinforcement.
            return None
        return eps_lo_arr[min_index][0]

    n_eps = Int(20, auto_set=False, enter_set=True)
    eps_range = Property(depends_on='n_eps,modified')
    @cached_property
    def _get_eps_range(self):
        eps_cu = self.eps_cu
        eps_ccu = 0.8 * eps_cu
        env_reinf = self.strain_env_reinf

        if env_reinf:
            '''Strain envelope for reinforced cross section
            '''
            eps_t_lo = env_reinf.convert_eps_u_2_lo(eps_up=eps_cu)
            eps_t_lo_0 = env_reinf.convert_eps_u_2_lo(eps_up=0.)
            eps_t_u = env_reinf.material_law_.eps_u

            # Strain arrays for the lower rim
            eps_cc_0 = np.linspace(eps_ccu, 0., self.n_eps)
            eps_0_tlo = np.linspace(0., eps_t_lo, self.n_eps)
            eps_tlo_tlo0 = np.linspace(eps_t_lo, eps_t_lo_0, self.n_eps)
            eps_tlo0_tu = np.linspace(eps_t_lo_0, eps_t_u, self.n_eps)

            # Strain arrays for the upper rim
            eps_cc_c = np.linspace(eps_ccu, eps_cu, self.n_eps)
            eps_c_const = self.eps_cu * np.ones_like(eps_cc_0)
            eps_c_0 = np.linspace(eps_cu, 0., self.n_eps)
            eps_0_tu = np.linspace(0., eps_t_u, self.n_eps)

            eps1 = np.vstack([eps_cc_0, eps_cc_c])
            eps2 = np.vstack([eps_0_tlo, eps_c_const])
            eps3 = np.vstack([eps_tlo_tlo0, eps_c_0])
            eps4 = np.vstack([eps_tlo0_tu, eps_0_tu])

            return np.hstack([eps1, eps2, eps3, eps4])
        else:
            '''Strain envelope for cross section without reinforcement
            '''
            # Strain arrays for the lower rim
            eps_cc_0 = np.linspace(eps_ccu, 0., self.n_eps)
            eps_00 = np.zeros_like(eps_cc_0)

            # Strain arrays for the upper rim
            eps_cc_c = np.linspace(eps_ccu, eps_cu, self.n_eps)
            eps_c_0 = np.linspace(eps_cu, 0., self.n_eps)

            eps1 = np.vstack([eps_cc_0, eps_cc_c])
            eps2 = np.vstack([eps_00, eps_c_0])

            return np.hstack([eps1, eps2])

    n_eps_range = Property(depends_on='n_eps,modified')
    @cached_property
    def _get_n_eps_range(self):
        return self.eps_range.shape[1]

    #===========================================================================
    # MN Diagram
    #===========================================================================

    def _get_MN_fn(self, eps_lo, eps_up):
        self.cs.set(eps_lo=eps_lo,
                    eps_up=eps_up)
        return (self.cs.M, self.cs.N)

    MN_vct = Property()
    def _get_MN_vct(self):
        return np.vectorize(self._get_MN_fn)

    MN_arr = Property(depends_on='modified,n_eps')
    @cached_property
    def _get_MN_arr(self):
        return self.MN_vct(self.eps_range[0, :], self.eps_range[1, :])

    #===========================================================================
    # f_eps Diagram
    #===========================================================================

    current_eps_idx = Int(1)  # , auto_set = False, enter_set = True)

    current_eps = Property(depends_on='current_eps_idx,modified')
    @cached_property
    def _get_current_eps(self):
        return self.eps_range[(0, 1), self.current_eps_idx - 1]

    current_MN = Property(depends_on='current_eps_idx,modified')
    @cached_property
    def _get_current_MN(self):
        return self._get_MN_fn(*self.current_eps)

    def plot_eps(self, ax):
        ax.plot(-self.eps_range,
                [0, self.cs.matrix_cs_with_state.geo.height],
                color='black')
        ax.plot(-self.current_eps,
                [0, self.cs.matrix_cs_with_state.geo.height],
                lw=3, color='red')

        ax.spines['left'].set_position('zero')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.spines['left'].set_smart_bounds(True)
        ax.spines['bottom'].set_smart_bounds(True)
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

    def plot_MN(self, ax):
        ax.plot(self.MN_arr[0], -self.MN_arr[1], lw=2, color='blue')
        ax.plot(self.current_MN[0], -self.current_MN[1], 'g.',
                markersize=20.0, color='red')

        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.spines['left'].set_smart_bounds(True)
        ax.spines['bottom'].set_smart_bounds(True)
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')
        ax.grid(b=None, which='major')
        x1, x2, z1, z2 = ax.axis()
        ax.axis([0, x2, z1, z2])

    def plot_custom(self, ax, color='blue', linestyle='-',
                    linewidth=2, label='<unnamed>'):
        M = self.MN_arr[0]
        N = -self.MN_arr[1]
        ax.plot(M, N, lw=linewidth, color=color,
                ls=linestyle, label=label)

        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')
        ax.spines['left'].set_smart_bounds(True)
        ax.spines['bottom'].set_smart_bounds(True)
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')
        ax.grid(b=None, which='major')
        x1, x2, z1, z2 = ax.axis()
        z_min = np.min(np.hstack([[z1], N]))
        z_max = np.max(np.hstack([[z2], N]))
        x_max = np.max(np.hstack([[x2], M]))
        ax.axis([0, x_max, z_min, z_max])

    #===========================================================================
    # Visualisation related attributes
    #===========================================================================

    def plot(self, fig):
        ax1 = fig.add_subplot(1, 2, 1)
        self.plot_eps(ax1)
        ax2 = fig.add_subplot(1, 2, 2)
        self.plot_MN(ax2)

    node_name = 'MxN diagram'

    tree_view = View(Group(
                HGroup(
                Group(Item('n_eps', springy=True),
                      Item('current_eps_idx', editor=RangeEditor(low=1,
                                   high_name='n_eps_range',
                                   format='(%s)',
                                   mode='slider',
                                   auto_set=False,
                                   enter_set=False,
                                   ),
                           show_label=False,
                           ),
                      label='Discretization',
                      springy=True
                      ),
                springy=True,
                ),
                scrollable=True,
                ),
                width=1.0,
                height=0.8,
                resizable=True,
                buttons=['OK', 'Cancel'])

if __name__ == '__main__':
    pass
