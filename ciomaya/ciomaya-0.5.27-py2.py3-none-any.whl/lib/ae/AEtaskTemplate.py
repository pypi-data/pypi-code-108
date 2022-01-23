"""
Handle the UI for extra assets:
"""

import pymel.core as pm
from ciomaya.lib import const as k
from ciomaya.lib.ae import AEcommon


def create_ui(node_attr):
    """Build static UI"""
 
    with AEcommon.ae_template():
        grp = pm.textFieldGrp("taskTemplateGrp", label="Task Template")
        label = pm.layout(grp, q=True, childArray=True)[0]
        pm.popupMenu(parent=label)
        pm.menuItem(label="Reset")
        populate_ui(node_attr)

def populate_ui(node_attr):
    """Populate / reconfigure UI for the current node"""
    attr = pm.Attribute(node_attr)
    widgets = _get_widgets()
    # index 2 is the field. (1 is the label) 
    pm.connectControl(widgets["field"], attr, index=2)
    # reconfigure the popup for this node.
    item = pm.popupMenu(widgets["popup_menu"], q=True, itemArray=True)[0]
    pm.menuItem(item, edit=True, command=pm.Callback(_on_reset, attr))

def _get_widgets(parent=None):
    if not parent:
        parent = pm.setParent(q=True)
    field_grp = AEcommon.find_ui("taskTemplateGrp", parent)
    label = pm.layout(field_grp, q=True, childArray=True)[0]

    return {
        "field": field_grp,
        "popup_menu": pm.control( label, q=True, popupMenuArray=True)[0]
    }

def _on_reset(attribute):
    attribute.set(k.DEFAULT_TEMPLATE)
 