from bmcs_utils.api import Model, Int, Item, View, IntEditor
from bmcs_beam.beam_config.system.anastruct.anastruct_custom_plotter import CustomPlotter
import traits.api as tr
from anastruct import SystemElements

class System(Model):

    name = 'System'

    n_per_element = Int(50, desc='Postprocessing mesh size per element. Has no influence on the fe calculation.',
                        SYSTEM=True)
    tree = []

    ipw_view = View(
        Item('n_per_element', latex='n_\mathrm{per~elem}', editor=IntEditor(min=10)),
    )

    @tr.observe("+SYSTEM")
    def _update_struct_state(self, event):
        self.update_struct()

    def update_struct(self):
        return NotImplementedError

    def get_new_struct(self):
        struct = SystemElements()
        struct.plotter = CustomPlotter(struct, mesh=self.n_per_element)
        return struct