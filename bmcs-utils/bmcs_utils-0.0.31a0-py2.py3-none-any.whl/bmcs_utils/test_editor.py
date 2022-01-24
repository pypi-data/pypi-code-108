from bmcs_utils.trait_types import \
    Float, Int, Bool, FloatRangeEditor, Range, ProgressEditor
from bmcs_utils.model import Model
from bmcs_utils.item import Item
from bmcs_utils.view import View
from bmcs_utils.editors import SelectionEditor
import numpy as np
import time
import traits.api as tr

class CSShape(Model):

    def update_plot(self, axes):
        pass

class Rectangle(CSShape):
    H = Float(10, desc=r'first material parameter')
    B = Float(5, desc='input parameter')

    ipw_view = View(
        Item('H'),
        Item('B')
    )

class Circle(CSShape):
    R = Float(10, desc=r'first material parameter')

    ipw_view = View(
        Item('R'),
    )

class ExampleModel(Model):
    name = 'Example'

    a = Float(0, desc=r'first material parameter')
    b = Int(5, desc='input parameter')
    c = Bool(True)
    t = Float(0)
    t_max = Float(10)
    sim_stop = Bool(False)

    options = tr.Dict(
        {
            'rectangle': Rectangle(),
            'circle': Circle()
        }
    )

    shape = tr.Instance(CSShape)
    def _shape_default(self):
        return self.options['rectangle']

#    shape = tr.Either(Rectangle,Circle)

    ipw_view = View(
        Item('t', editor=ProgressEditor(run_method='run',
                                        reset_method='reset',
                                        interrupt_var='sim_stop',
                                        time_var='t',
                                        time_max='t_max',
                                        )
             ),
        Item('a', editor=FloatRangeEditor(low=0, high=10)),
        Item('shape', editor=SelectionEditor(options_trait='options')),
        Item('b', latex=r'\beta', readonly=True),
        Item('t_max', latex=r'\theta'),
        Item('c', latex=r'\gamma')
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
        axes.plot(t_arr, np.sin(t_arr) )

