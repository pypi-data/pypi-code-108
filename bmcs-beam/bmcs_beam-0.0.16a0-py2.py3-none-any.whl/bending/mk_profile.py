from bmcs_cross_section.mkappa import MKappa
from bmcs_utils.api import InteractiveModel, View
import traits.api as tr

class MKappaProfile(InteractiveModel):
    name = 'M-K Profile'

    mc = tr.Instance(MKappa, ())

    ipw_view = View(

    )

    def subplots(self, fig):
        return fig.subplots(1, 1)

    def update_plot(self, axes):
        ax1 = axes

        ax1.plot(self.mc.kappa_t, self.mc.M_t)
        ax1.set_xlabel('Kappa')
        ax1.set_ylabel('Moment')
        ax1.grid(True)