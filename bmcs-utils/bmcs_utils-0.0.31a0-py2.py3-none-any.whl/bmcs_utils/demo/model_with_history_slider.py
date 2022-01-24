from bmcs_utils.trait_types import \
    Float, Int, Bool, Instance, Range
from bmcs_utils.editors import \
    HistoryEditor
from bmcs_utils.model import Model
from bmcs_utils.item import Item
from bmcs_utils.view import View
import bmcs_utils.api as bu
import numpy as np

class ModelWithHistory(Model):
    """Example model with a cross sectional shape"""
    name = 'Example'

    b = Int(5, desc='input parameter')
    t = Float(0)
    t_max = Float(10)

    ipw_view = View(
        Item('b', latex=r'\beta', readonly=True),
        Item('t', latex=r't', readonly=True),
        Item('t_max', latex=r'\theta'),
        time_editor=HistoryEditor(var='t',
                                 max_var='t_max',
        )
    )

    exponent = bu.Float(1)
    def update_plot(self, axes):
        with bu.print_output:
            print('SELF', self)
        x_range = np.linspace(0,self.t_max,100)
        y_range = x_range**self.exponent
        axes.plot(x_range, y_range)
        y_val = self.t**self.exponent
        axes.plot(self.t,y_val,marker='o')

class TwoModelsWithHistory(Model):
    mwh1 = Instance(ModelWithHistory)
    def _mwh1_default(self):
        return ModelWithHistory(exponent=1)

    mwh2 = Instance(ModelWithHistory)
    def _mwh2_default(self):
        return ModelWithHistory(exponent=4)

    tree = ['mwh1', 'mwh2']

    def update_plot(self, axes):
        with bu.print_output:
            print('mhwh1')