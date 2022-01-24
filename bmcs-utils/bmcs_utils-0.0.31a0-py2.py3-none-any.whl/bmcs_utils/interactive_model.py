
import traits.api as tr
from bmcs_utils.app_window import AppWindow
from bmcs_utils.i_model import IModel

import k3d

@tr.provides(IModel)
class InteractiveModel(tr.HasTraits):
    """Base class for interactive bmcs_utils
    """

    name = tr.Str("<unnamed>")

    plot_backend = 'mpl'
    """"plot_backend = 'mpl' or 'k3d'"""

    def subplots(self, fig):
        if self.plot_backend == 'mpl':
            return fig.subplots(1, 1)
        elif self.plot_backend == 'k3d':
            return fig
        else:
            raise NameError(self.plot_backend + ' is not a valid plot_backend!')

    def plot(self, axes):
        """Alias to update plot - to be overloaded by subclasses"""
        self.update_plot(axes)

    def update_plot(self, axes):
        raise NotImplementedError()

    def interact(self):
        return AppWindow(self).interact()
