from bmcs_utils.trait_types import \
    Float, Int, Bool, FloatRangeEditor, Instance, \
    Range, ProgressEditor, FloatEditor, EitherType
from bmcs_utils.model import Model
from bmcs_utils.item import Item
from bmcs_utils.view import View
import numpy as np
import time
from bmcs_utils.demo.shape_model import Rectangle, CSShape, Circle
from bmcs_utils.demo.layout_model import LayoutModel

class ModelWithProgressBar(Model):
    """Example model with a cross sectional shape"""
    name = 'Example'

    b = Int(5, desc='input parameter')
    c = Bool(True)
    t = Float(0)
    t_max = Float(10)
    sim_stop = Bool(False)

    a = Float(0.0, desc=r'first material parameter')
    kappa_slider = Float(0.0000001)

    shape = EitherType(options=[('rectangle', Rectangle),
                                ('circle', Circle)])

    sin_model = Instance(LayoutModel, ())

    tree = ['shape', 'sin_model']
    ipw_view = View(
        Item('b', latex=r'\beta', readonly=True),
        Item('t_max', latex=r'\theta'),
        Item('c', latex=r'\gamma'),
        Item('a', latex=r'a'),
        Item('kappa_slider', latex='\kappa', editor=FloatRangeEditor(low=0, high=20, n_steps=100)),
        Item('shape'),  # editor=SelectionEditor(options_trait='options')),
        time_editor=ProgressEditor(run_method='run',
                                   reset_method='reset',
                                   interrupt_var='sim_stop',
                                   time_var='t',
                                   time_max='t_max',
        )
    )

    def run(self):
        self.a += 1
        t_arr = np.linspace(self.t, self.t_max, 50)
        for t in t_arr:
            # allow for the interference by the editor
            if self.sim_stop:
                break
            time.sleep(0.1)
            self.t = t

    def reset(self):
        self.trait_set(a=0, b=5, c=True, t=0)

    def subplots(self, fig):
        axes = fig.subplots(1,1)
        axes.set_ylim(ymin=-1.05, ymax=1.05)
        axes.set_xlim(xmin=0, xmax=self.t_max)
        return axes

    def update_plot(self, axes):
        t_arr = np.linspace(0, self.t, 100)
        axes.plot(t_arr, np.cos(t_arr) )

