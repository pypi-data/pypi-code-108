"""
Handle the UI for emails:
"""

import pymel.core as pm
from ciomaya.lib import const as k

from ciomaya.lib.ae import AEcommon


def create_ui(node_attr):
    """Build static UI."""
    with AEcommon.ae_template():

        pm.rowLayout(
            numberOfColumns=2,
            columnWidth2=(k.AE_TEXT_WIDTH, 210),
            columnAttach=((1, "right", 0), (2, "both", 0)),
        )
        pm.text(label="")
        pm.button("emailsAddButton", label="Add Email Address", height=24)
        #  command=pm.Callback(on_add_btn, node)
        pm.setParent("..")  # out rowLayout
        pm.separator()

        pm.columnLayout("emailsColumn", adj=True)

        pm.setParent("..")  # out columnLayout

        populate_ui(node_attr)


def populate_ui(node_attr):
    """Reconfigure action buttons when node changes."""

    attr = pm.Attribute(node_attr)
    widgets = _get_widgets()

    pm.button(widgets["button"], edit=True,
              command=pm.Callback(_on_add_btn, attr))

    for widget in pm.columnLayout(widgets["column"], q=True, childArray=True) or []:
        pm.deleteUI(widget)

    pm.setParent(widgets["column"])
    for i, attr_element in enumerate(attr):

        address_att = attr_element.attr("emailAddress")
        active_att = attr_element.attr("emailAddressActive")

        label_ctl = pm.text(label="Email: {:d}".format(i + 1))

        address_ctl = pm.textField()
        active_ctl = pm.checkBox(label="")

        del_ctl = pm.symbolButton(
            image="smallTrash.xpm", command=pm.Callback(_on_remove_email, attr_element)
        )

        _form_layout(label_ctl, address_ctl, active_ctl, del_ctl)

        pm.connectControl(active_ctl, active_att)
        pm.connectControl(address_ctl, address_att)

        _setup_script_jobs(active_att, address_ctl)

        _active_cb_changed(active_att, address_ctl)

        pm.setParent(widgets["column"])


def _get_widgets(parent=None):
    if not parent:
        parent = pm.setParent(q=True)
    return {
        "button":  AEcommon.find_ui("emailsAddButton", parent),
        "column":  AEcommon.find_ui("emailsColumn", parent)
    }


def _setup_script_jobs(active_att, address_ctl):

    pm.scriptJob(
        attributeChange=(
            active_att,
            pm.Callback(_active_cb_changed, active_att, address_ctl),
        ),
        parent=address_ctl,
        replacePrevious=True
    )


def _on_add_btn(attr):
    AEcommon.next_available_element_plug(attr).attr("emailAddress").set("")


def _active_cb_changed(att, ctl):
    pm.textField(ctl, edit=True, enable=att.get())


def _on_remove_email(attr):
    pm.removeMultiInstance(attr, b=True)


def _form_layout(*widgets):
    # There must be 4 widgets.
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
