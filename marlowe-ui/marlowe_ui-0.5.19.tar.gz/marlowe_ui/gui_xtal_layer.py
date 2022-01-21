from . import tktool

from . import guidata

from . import gui_xtal_layer_elem as elem

XtalLayer = tktool.oneof.OneofFactory(elem.XtalLayerElem,
                                      guidata.xtal_layer_elem_default)
