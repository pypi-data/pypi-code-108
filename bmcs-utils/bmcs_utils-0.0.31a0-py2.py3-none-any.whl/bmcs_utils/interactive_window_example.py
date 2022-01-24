
from bmcs_utils.app_window import AppWindow
from bmcs_utils.model import Model
from bmcs_utils.view import View
from bmcs_utils.item import Item


from bmcs_utils.trait_types import \
    Float, FloatEditor

class Model(Model):
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
