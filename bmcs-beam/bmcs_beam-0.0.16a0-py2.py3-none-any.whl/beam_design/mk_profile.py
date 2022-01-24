from bmcs_beam.moment_curvature.moment_curvature import MomentCurvature
from bmcs_utils.api import InteractiveModel, View


class MomentCurvatureProfile(InteractiveModel):
    name = 'M_K Profile'
    mc = MomentCurvature(kappa_range=(-0.0002, 0.0002, 100),
        idx=25, n_m=100)

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