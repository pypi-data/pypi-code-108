from .tktool import oneof

from . import guidata

from . import gui_proj_elem

Proj = oneof.OneofFactory(gui_proj_elem.ProjElem,
                          guidata.proj_elem_default)
