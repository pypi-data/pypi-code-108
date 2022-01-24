import numpy as np
import traits.api as tr
from bmcs_utils.api import \
    InteractiveModel, Item, View, Float, Int, FloatEditor, EitherType, EitherTypeEditor
from bmcs_cross_section.matmod import ReinfMatMod, SteelReinfMatMod, CarbonReinfMatMod


class ReinfLayer(InteractiveModel):
    # TODO: changes in the ipw interactive window doesn't reflect on mkappa
    #  (maybe because these are lists and changing the elements doesn't notify)
    name = 'Reinf layer'

    cs_layout = tr.WeakRef

    z = Float(50, CS=True)
    """z positions of reinforcement layers"""

    P = Float(100, CS=True)
    """Perimeter"""

    A = Float(100, CS=True)
    """Cross sectional area"""

    matmod = EitherType(options=[('steel', SteelReinfMatMod),
                                 ('carbon', CarbonReinfMatMod)])

    ipw_view = View(
        Item('matmod', latex=r'\mathrm{behavior}', editor=EitherTypeEditor(show_properties=False)),
        Item('z', latex='z \mathrm{[mm]}'),
        Item('A', latex='A \mathrm{[mm^2]}'),
    )

    tree = ['matmod']

    def get_N(self, eps):
        return self.A * self.matmod_.get_sig(eps)

    def update_plot(self, ax):
        eps_range = self.matmod_.get_eps_plot_range()
        N_range = self.get_N(eps_range)
        ax.plot(eps_range, N_range, color='red')
        ax.fill_between(eps_range, N_range, 0, color='red', alpha=0.1)
        ax.set_xlabel(r'$\varepsilon$ [-]')
        ax.set_ylabel(r'$F$ [N]')


class FabricLayer(ReinfLayer):
    """Reinforcement with a grid structure
    """
    name = 'Fabric layer'
    width = Float(100, CS=True)
    spacing = Float(14, CS=True)
    A_roving = Float(1, CS=True)

    A = tr.Property(Float, depends_on='+CS')
    """cross section area of reinforcement layers"""
    @tr.cached_property
    def _get_A(self):
        return int(self.width/self.spacing) * self.A_roving

    P = tr.Property(Float, depends_on='+CS')
    """cross section area of reinforcement layers"""
    @tr.cached_property
    def _get_P(self):
        raise NotImplementedError

    def _matmod_default(self):
        return 'carbon'

    ipw_view = View(
        Item('matmod', latex=r'\mathrm{behavior}'),
        Item('z', latex='z \mathrm{[mm]}'),
        Item('width', latex='\mathrm{fabric~width} \mathrm{[mm]}'),
        Item('spacing', latex='\mathrm{rov~spacing} \mathrm{[mm]}'),
        Item('A_roving', latex='A_r \mathrm{[mm^2]}'),
        Item('A', latex=r'A [mm^2]', readonly=True),
    )


class BarLayer(ReinfLayer):
    """"Layer consisting of discrete bar reinforcement"""
    name = 'Bar layer'
    ds = Float(16, CS=True)
    count = Int(1, CS=True)

    A = tr.Property(Float, depends_on='+CS')
    """cross section area of reinforcement layers"""
    @tr.cached_property
    def _get_A(self):
        return self.count * np.pi * (self.ds / 2.) ** 2

    P = tr.Property(Float, depends_on='+CS')
    """permeter of reinforcement layers"""
    @tr.cached_property
    def _get_P(self):
        return self.count * np.pi * (self.ds)

    def _matmod_default(self):
        return 'steel'

    ipw_view = View(
        Item('matmod', latex=r'\mathrm{behavior}'),
        Item('z', latex=r'z \mathrm{[mm]}'),
        Item('ds', latex=r'ds \mathrm{[mm]}'),
        Item('count', latex='count'),
        Item('A', latex=r'A [mm^2]'),
    )
