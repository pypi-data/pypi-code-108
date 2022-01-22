"""
Handle the UI for projects:

"""

import pymel.core as pm
from ciocore import data as coredata
from ciomaya.lib import const as k
from ciomaya.lib.ae import AEcommon


def create_ui(node_attr):
    """Build static UI"""

    with AEcommon.ae_template():

        pm.rowLayout(
            numberOfColumns=2,
            columnWidth2=(k.AE_TEXT_WIDTH, 300),
            columnAttach=((1, "right", 0), (2, "both", 0)),
        )

        pm.text("projectMenuLabel", label="Conductor project")
        pm.optionMenu("projectMenu", acc=True)


        pm.setParent("..")

        populate_ui(node_attr)


def populate_ui(node_attr):
    """Populate / reconfigure UI for the current node"""
    attr = pm.Attribute(node_attr)
    widgets = _get_widgets()

    if not coredata.valid():
        for item in pm.optionMenu(widgets["menu"], q=True, itemListLong=True):
            pm.deleteUI(item)
        pm.setParent(widgets["menu"], menu=True)
        pm.menuItem(label="Not connected")

    pm.optionMenu(widgets["menu"], edit=True, changeCommand=pm.Callback(
        _set_project_value, attr, widgets["menu"]))

    # Update this UI if the attribute changes by some other means
    # For example: setAttr, or another instance of the attribute editor.
    _setup_script_jobs(attr, widgets)

    pm.evalDeferred(pm.Callback(_ensure_connection, attr, widgets))


def _get_widgets(parent=None):
    if not parent:
        parent = pm.setParent(q=True)
    return {
        "menu": AEcommon.find_ui("projectMenu", parent)
    }


def _setup_script_jobs(attr, widgets):
    menu = widgets["menu"]

    pm.scriptJob(
        attributeChange=(
            attr,
            pm.Callback(AEcommon.sync_menu_to_attr, menu, attr),
        ),
        parent=menu,
        replacePrevious=True
    )


def _ensure_connection(attr, widgets):
    """Fetch a fresh list of projects from Conductor.

    Use cached data on the module if force is False"""
    project_data = coredata.data()["projects"]
    AEcommon.ensure_populate_menu(widgets["menu"], project_data)

    AEcommon.sync_menu_to_attr(widgets["menu"], attr)


def _set_project_value(attr, menu):
    """
    Respond to menu change.
    """
    num_items = pm.optionMenu(menu, q=True, numberOfItems=True)
    if not num_items:
        return
    selected_value = pm.optionMenu(menu, q=True, value=True)
    if attr.get() != selected_value:
        attr.set(selected_value)
        AEcommon.print_setAttr_cmd(attr)
