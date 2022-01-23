"""
Handle the UI for environment:
"""

import pymel.core as pm
from ciomaya.lib import const as k
from ciomaya.lib.ae import AEcommon


def create_ui(node_attr):
    """Build static UI."""
    with AEcommon.ae_template():
 
        pm.rowLayout(
            width=290,
            numberOfColumns=2,
            columnWidth2=(k.AE_TEXT_WIDTH, 210),
            columnAttach=((1, "right", 0), (2, "both", 0)),
        )

        pm.text(label="")
        pm.button("metadataAddButton",label="Add Metadata Entry", height=24 )
        pm.setParent("..")  # out rowLayout
        pm.separator()

        _form_layout(pm.text(label="Key", align="left", width=k.AE_TEXT_WIDTH),
                     pm.text(label="Value", align="left"),
                     pm.text(label="", width=36)
                     )
        
        pm.setParent("..")  # out _form_layout

        pm.columnLayout("metadataColumn", adj=True)

        pm.setParent("..")  # out columnLayout

        populate_ui(node_attr)




def populate_ui(node_attr):
    """Reconfigure action buttons when node changes."""

    attr = pm.Attribute(node_attr)
    widgets = _get_widgets()

    pm.button(widgets["button"], edit=True,
              command=pm.Callback(_add_entry, attr))

    for widget in pm.columnLayout(widgets["column"], q=True, childArray=True) or []:
        pm.deleteUI(widget)

    pm.setParent(widgets["column"])
    for attr_element in attr:

        key_att = attr_element.attr("metadataKey")
        val_att = attr_element.attr("metadataValue")

        key_ctl = pm.textField(placeholderText="METADATA_KEY", width=k.AE_TEXT_WIDTH)
        val_ctl = pm.textField(placeholderText="METADATA_VALUE")
        del_ctl = pm.symbolButton(
            image="smallTrash.xpm", width=36, command=pm.Callback(_remove_entry, attr_element)
        )

        _form_layout(key_ctl, val_ctl, del_ctl)
        pm.setParent("..")  # out _form_layout


        pm.connectControl(key_ctl, key_att)
        pm.connectControl(val_ctl, val_att)

        pm.setParent(widgets["column"])

def _get_widgets(parent=None):
    if not parent:
        parent = pm.setParent(q=True)
    return {
        "button":  AEcommon.find_ui("metadataAddButton", parent),
        "column":  AEcommon.find_ui("metadataColumn", parent)
    }



def _add_entry(attr):
    AEcommon.next_available_element_plug(attr).attr("metadataKey").set("")
 
def _remove_entry(attribute):
    pm.removeMultiInstance(attribute, b=True)


def _form_layout(*widgets):
    # There must be 3 widgets.
    form = pm.formLayout(nd=100)
    for widget in widgets:
        pm.control(widget, edit=True, parent=form)

    form.attachForm(widgets[0], "left", 2)
    form.attachNone(widgets[0], "right")
    form.attachForm(widgets[0], "top", 2)
    form.attachForm(widgets[0], "bottom", 2)

    form.attachControl(widgets[1], "left", 2, widgets[0])
    form.attachControl(widgets[1], "right", 2, widgets[2])
    form.attachForm(widgets[1], "top", 2)
    form.attachForm(widgets[1], "bottom", 2)

    form.attachNone(widgets[2], "left")
    form.attachForm(widgets[2], "right", 2)
    form.attachForm(widgets[2], "top", 2)
    form.attachForm(widgets[2], "bottom", 2)

    return form
