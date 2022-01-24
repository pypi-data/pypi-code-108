from models.trait_types import \
    Float, Int, Bool, FloatRangeEditor, Range
from models.interactive_window import InteractiveModel, Item, View
import numpy as np

class ExampleModel(InteractiveModel):
    name = 'Example'

    a = Float(0, desc=r'first material parameter')
    b = Int(5, desc='input parameter')
    c = Bool(True)
    t = Float(0)

    ipw_view = View(
        Item('a'),
        Item('b', latex=r'\beta'),
        Item('c'),
        Item('t', editor=FloatRangeEditor(min=0, max=10)),
        simulator='run',
    )

    def run(self, update_progress=lambda t:t):
        self.a += 1
        t_arr = np.linspace(0, 1, 10)
        for t in t_arr:
            update_progress(t)
            self.t = t

    def update_plot(self, axes):
        print('update_plot called')
        trait_names = self.trait_names()
        print(self.trait_get(trait_names))

ex = ExampleModel()
b = ex.trait('b').valxxx
print(b)
