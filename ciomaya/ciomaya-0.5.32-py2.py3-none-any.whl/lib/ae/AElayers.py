"""
Handle the UI for layers

"""
import pymel.core as pm
from ciomaya.lib import const as k
from ciomaya.lib.ae import AEcommon


def create_ui(node_attr):
    """Build static UI.

    Use a customUI because:
    1. TODO: Don't give user the ability to override layers.
    2. TODO: Provide our own custom popup.
    3. TODO: Info list of the layers that will be rendered.
    """
    with AEcommon.ae_template():
        
       
        pm.rowLayout(
                     numberOfColumns=2,
                     columnWidth2=(k.AE_TEXT_WIDTH, 200),
                     columnAttach=((1, "right", 0), (2, "both", 0))
                     )

        pm.text(label="Render Layers")
        pm.attrEnumOptionMenu("layersMenu", label="",  attribute=node_attr, width=200)
        pm.setParent("..")
        populate_ui(node_attr)


def populate_ui(node_attr):
    """Reconfigure action buttons when node changes."""
    widgets = _get_widgets()
    pm.attrEnumOptionMenu(widgets["menu"], edit=True, attribute=node_attr)


def _get_widgets(parent=None):
    if not parent:
        parent = pm.setParent(q=True)

    return {
        "menu":  AEcommon.find_ui("layersMenu", parent),
    }
 
 