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
        pm.button("environmentAddButton",
                  label="Add Environment Variable", height=24)
        pm.setParent("..")  # out rowLayout
        pm.separator()

        _form_layout(pm.text(label="Key", align="left", width=220),
                     pm.text(label="Value", align="left"),
                     pm.text(label="Excl", align="left", width=36),
                     pm.text(label="", width=36)
                     )

        pm.setParent("..")  # out _form_layout

        pm.columnLayout("environmentColumn", adj=True)

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

        key_att = attr_element.attr("extraEnvironmentKey")
        val_att = attr_element.attr("extraEnvironmentValue")
        exc_att = attr_element.attr("extraEnvironmentExclusive")

        key_ctl = pm.textField(
            placeholderText="VAR_NAME", width=220)
        val_ctl = pm.textField(placeholderText="Value")
        exc_ctl = pm.checkBox(label="", width=36)
        del_ctl = pm.symbolButton(
            image="smallTrash.xpm", width=36, command=pm.Callback(
                pm.removeMultiInstance, attr_element, b=True
            )
        )

        _form_layout(key_ctl, val_ctl, exc_ctl, del_ctl)
        pm.setParent("..")  # out _form_layout

        pm.connectControl(key_ctl, key_att)
        pm.connectControl(val_ctl, val_att)
        pm.connectControl(exc_ctl, exc_att)

        pm.setParent(widgets["column"])


def _get_widgets(parent=None):
    if not parent:
        parent = pm.setParent(q=True)
    return {
        "button":  AEcommon.find_ui("environmentAddButton", parent),
        "column":  AEcommon.find_ui("environmentColumn", parent)
    }


def _add_entry(attr):
    AEcommon.next_available_element_plug(
        attr).attr("extraEnvironmentKey").set("")


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
    form.attachControl(widgets[2], "right", 2, widgets[3])
    form.attachForm(widgets[2], "top", 2)
    form.attachForm(widgets[2], "bottom", 2)

    form.attachNone(widgets[3], "left")
    form.attachForm(widgets[3], "right", 2)
    form.attachForm(widgets[3], "top", 2)
    form.attachForm(widgets[3], "bottom", 2)

    return form



def on_add_btn(node):
    indices = node.attr("extraEnvironment").getArrayIndices()
    next_available = next(a for a, b in enumerate(indices + [-1]) if a != b)
    node.attr("extraEnvironment")[next_available].attr(
        "extraEnvironmentKey").set("")
    node.attr("extraEnvironment")[next_available].attr(
        "extraEnvironmentValue").set("")


def on_text_changed(text_field, attribute):
    val = pm.textField(text_field, q=True, text=True)
    attribute.set(val)


def on_excl_cb_changed(checkbox, attribute):
    val = pm.checkBox(checkbox, q=True, value=True)
    attribute.set(val)


def on_remove_var(attribute):
    pm.removeMultiInstance(attribute, b=True)
