import numpy as np
import traits.api as tr
from bmcs_utils.api import \
    InteractiveModel, View, Item, EitherType, ModelList, List
from .cs_reinf_layer import ReinfLayer

class CrossSectionLayout(ModelList):
    name = 'Cross Section Layout'

    items = List(ReinfLayer, [])

    cs_design = tr.WeakRef

    def add_layer(self, rl):
        rl.cs_layout = self
        self.items.append(rl)

    z_j = tr.Property
    def _get_z_j(self):
        return np.array([r.z for r in self.items], dtype=np.float_)

    p_j = tr.Property
    '''
    Get the perimeter
    '''
    def _get_p_j(self):
        return np.array([r.p for r in self.items], dtype=np.float_)

    A_j = tr.Property
    def _get_A_j(self):
        return np.array([r.A for r in self.items], dtype=np.float_)

    def get_N_tj(self, eps_tj):
        return np.array([r.get_N(eps_t)
                         for r, eps_t in zip(self.items, eps_tj.T)],
                         dtype=np.float_).T

    ipw_view = View(
    )

    def subplots(self, fig):
        return fig.subplots(1, 1)

    def plot_csl(self, ax):
        self.cs_design.cross_section_shape_.update_plot(ax)

        H = int(self.cs_design.cross_section_shape_.H)

        maxA = 0
        for layer in self.items:
            A = layer.A
            maxA = max(A, maxA)

        for layer in self.items:
            z = layer.z
            A = layer.A
            b = self.cs_design.cross_section_shape_.get_b([z])
            ax.plot([-0.9 * b/2, 0.9 * b/2], [z, z], color='r',
                    linewidth=5 * A/maxA)

        # ax.annotate(
        #     'E_composite = {} GPa'.format(np.round(self.get_comp_E() / 1000), 0),
        #     xy=(-H / 2 * 0.8, (H / 2 + H / 2) * 0.8), color='blue'
        # )

    def update_plot(self, ax):
        self.plot_csl(ax)