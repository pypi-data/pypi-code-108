
from bmcs_utils.app_window import \
    InteractiveModel, View, Item, AppWindow

from bmcs_utils.bmcs_utils.trait_types import \
    Float, FloatEditor

class Model(InteractiveModel):
    a = Float(20)
    b = Float(80)

    ipw_view = View(
        Item('a', latex='a', editor=FloatEditor()),
        Item('b', latex='b')
    )


m = Model()

ii = AppWindow(m)

print(
    ii.ipw_model_tabs[0].get_editors()
)
