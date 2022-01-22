"""
Handle the UI for instanceTypes:

"""

import maya.app.renderSetup.model.renderSetup as rs
import maya.app.renderSetup.views.overrideUtils as ov_utils
import pymel.core as pm
from ciocore import data as coredata

from ciomaya.lib import const as k
from ciomaya.lib.ae import AEcommon
 
def create_ui(node_attr):
    """Build static UI"""
    with AEcommon.ae_template():

        pm.rowLayout(
            numberOfColumns=2,
            columnWidth2=(k.AE_TEXT_WIDTH, 400),
            columnAttach=((1, "both", 0), (2, "both", 0)),
        )

        label = pm.text("instanceTypesLabel",label="Instance Type Name")
        pm.optionMenu("instanceTypesMenu", acc=True)
        popup = pm.popupMenu(parent=label)
        pm.setParent(popup, menu=True)
        pm.menuItem(label="Create Absolute Override for Visible Layer")

        pm.setParent("..")  # out of rowLayout

        populate_ui(node_attr)


def populate_ui(node_attr):
    """Reconfigure UI for the current node"""
    attr = pm.Attribute(node_attr)
    widgets = _get_widgets()
 
    if not  coredata.valid():
        for item in pm.optionMenu(widgets["menu"], q=True, itemListLong=True):
            pm.deleteUI(item)
        pm.setParent(widgets["menu"], menu=True)
        pm.menuItem(label="Not connected")

    # update popup menu items
    _configure_popup_menu(attr, widgets)

    pm.optionMenu(widgets["menu"], edit=True, changeCommand=pm.Callback(
        _set_instance_type_value, attr, widgets["menu"]))
    # Update this UI if the attribute changes by some other means
    # For example: setAttr, or another instance of the attribute editor.
    _setup_script_jobs(attr, widgets)

    _set_label_color(attr, widgets["label"])

    pm.evalDeferred(pm.Callback(_ensure_connection, attr, widgets))


def _configure_popup_menu(attr, widgets):
    override_item = pm.popupMenu(
        widgets["popup_menu"], q=True, itemArray=True)[0]

    enable_override = (
        pm.editRenderLayerGlobals(query=True, currentRenderLayer=True)
        != "defaultRenderLayer"
    )
    pm.menuItem(override_item, edit=True, en=enable_override, 
      command=pm.Callback(_create_layer_override, attr, widgets["label"]) )
 

def _get_widgets(parent=None):
    if not parent:
        parent = pm.setParent(q=True)
    label = AEcommon.find_ui("instanceTypesLabel", parent),
    return {
        "label" :label,
        "menu": AEcommon.find_ui("instanceTypesMenu", parent),
        "popup_menu": pm.control( label, q=True, popupMenuArray=True)[0]
    }



def _setup_script_jobs(attr, widgets):
    menu = widgets["menu"]

    pm.scriptJob(
        attributeChange=(
            attr,
            pm.Callback(_sync_menu_to_attr, attr, widgets),
        ),
        parent=menu,
        replacePrevious=True
    )

    pm.scriptJob(
        event=(
            "renderLayerManagerChange",
            pm.Callback(_on_render_layer_manager_change, attr, widgets),
        ),
        parent=menu,
    )


def _on_render_layer_manager_change(attr, widgets):

    _sync_menu_to_attr(attr, widgets)
    _set_label_color(attr, widgets["label"])


def _ensure_connection(attr, widgets, force=False):
    """Fetch a fresh list of inst types from Conductor (or the cache)."""

    instance_type_data = coredata.data(force_instance_types=force)["instance_types"]
    descriptions =  [t["description"] for t in instance_type_data]
    if len(descriptions) and isinstance(descriptions[0], list):
        descriptions = [v[0] for v in descriptions]

    AEcommon.ensure_populate_menu(widgets["menu"], descriptions)

    values =  [it["name"] for it in instance_type_data]
    AEcommon.sync_menu_to_attr(widgets["menu"], attr , values=values)


def _sync_menu_to_attr(attr, widgets):
    """
    Make sure menu item reflects the attribute value.

    If the attribute is invalid, set it to the first valid project.


    """
    menu = widgets["menu"]
    label = widgets["label"]
    
    items = pm.optionMenu(menu, q=True, itemListLong=True)
    if not items:
        return

    name = attr.get()
    index, instance_type = find_by_key("name", name)
    if not instance_type:
        pm.displayWarning("Didn't find '{}' in instance types".format(name))
        return

    one_based_index = index+1
    if one_based_index > len(items):
        one_based_index = 1
        attr.set(coredata.data()["instance_types"][0]["name"])

    pm.optionMenu(menu, edit=True, sl=one_based_index)

    _set_label_color(attr, label)


def _set_instance_type_value(attr, menu):
    """
    Respond to menu change.
    """
    num_items = pm.optionMenu(menu, q=True, numberOfItems=True)
    if not num_items:
        return
    description = pm.optionMenu(menu, q=True, value=True)
    _, instance_type = find_by_key("description", description)
    if not instance_type:
        pm.displayWarning("Didn't find '{}' in instance types".format(description))
        return

    name = instance_type["name"]
    if attr.get() != name:
        attr.set(name)
        AEcommon.print_setAttr_cmd(attr)


def _create_layer_override(attr, label):
    ov_utils.createAbsoluteOverride( attr.node().name(), attr.attrName(True) )
    _set_label_color(attr, label)



def _set_label_color(attr, label):
    """By convention, label is orange if attr has an override."""
    has_override = rs.hasOverrideApplied(
        attr.node().name(),  attr.attrName(True))
    text = "Instance Type Name"
    label_text = "<font color=#ec6a17>{}</font>".format(
        text) if has_override else text
    pm.text(label, edit=True, label=label_text)



def find_by_key(key, value):
    result = (None,None)
    if not coredata.valid():
        return result
    try:
        result = next(tup for tup in enumerate(coredata.data()["instance_types"]) if tup[1][key] == value)
    except StopIteration:
        pass
    return result
 
