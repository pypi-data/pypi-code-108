"""
Handle the UI for custom frames and use scout frames:

In both cases, when the use<Attrname> checkbox is unchecked,
the field is hidden.

"""

import pymel.core as pm
from ciomaya.lib import const as k
from ciomaya.lib.ae import AEcommon
import random

constants = {
    "customRange": {
        "text_label": "Custom Range",
        "annotation": "Specifies a set of frames to render. Provide a comma-separated list of progressions. Example 1,7,10-20,30-60x3,1001.",
        "bool_attr": "useCustomRange"
    },
    "scoutFrames": {
        "text_label": "Scout Frames",
        "annotation": "Specifies a set of frames to test render on Conductor before other frames. Provide a comma-separated list of progressions. Example 1,7,10-20,30-60x3,1001.",
        "bool_attr": "useScoutFrames"
    },
}


def create_ui(node_attr):
    """Build static UI.

    """
    attr = pm.Attribute(node_attr)
    key = attr.attrName(True)

    with AEcommon.ae_template():
        tflabel = constants[key]["text_label"]
        cblabel = "Use {}".format(tflabel)
        pm.checkBoxGrp("frameSpecCheckbox", label=cblabel)

        pm.frameLayout("frameSpecFrame",
                       visible=False, lv=False, cl=False, cll=False
                       )

        pm.textFieldGrp("frameSpecField", label=tflabel)

        pm.setParent("..")  # out of frameLayout
        populate_ui(node_attr)


def populate_ui(node_attr):
    """Reconfigure action buttons when node changes."""

    attr = pm.Attribute(node_attr)
    key = attr.attrName(True)
    widgets = _get_widgets()
    bool_attr = attr.node().attr(constants[key]["bool_attr"])
    bool_val = bool_attr.get()
    val = attr.get()

    pm.checkBoxGrp(
        widgets["checkbox"],
        edit=True,
        value1=bool_val,
        changeCommand=pm.Callback(
            _on_bool_changed, bool_attr, widgets["checkbox"],  widgets["frame"]),
    )

    pm.textFieldGrp(
        widgets["field"],
        edit=True,
        text=val,
        changeCommand=pm.Callback(
            _on_text_changed, attr,  widgets["field"]),
    )

    _on_bool_changed(bool_attr,  widgets["checkbox"], widgets["frame"])


def _get_widgets(parent=None):
    if not parent:
        parent = pm.setParent(q=True)
    return {
        "checkbox": AEcommon.find_ui("frameSpecCheckbox", parent),
        "frame":  AEcommon.find_ui("frameSpecFrame", parent),
        "field":  AEcommon.find_ui("frameSpecField", parent),
    }


def _on_bool_changed(attr, checkbox, frame):
    val = pm.checkBoxGrp(checkbox, q=True, value1=True)
    attr.set(val)
    pm.frameLayout(frame, edit=True, enable=True, visible=val)


def _on_text_changed(attr, widget):
    attr.set(pm.textFieldGrp(widget, q=True, text=True))
    AEcommon.print_setAttr_cmd(attr)
