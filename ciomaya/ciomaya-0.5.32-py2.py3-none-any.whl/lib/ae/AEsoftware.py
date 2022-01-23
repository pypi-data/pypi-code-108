"""
Handle the UI for 2 attributes:

1. hostSoftware (single value maya version)
2. pluginSoftware (multi value plugin name and version)

TODO: Try to move ALL the plugin/host compatibility logic out of this file.
"""

import pymel.core as pm
from ciocore import data as coredata
from ciomaya.lib import software
from ciomaya.lib import const as k
from ciomaya.lib.ae import AEcommon


def create_ui(node_attr):
    """Build static UI.

    A rowLayout for the host.
    A columnLayout for the plugins.
    """
    with AEcommon.ae_template():

        label = pm.text("hostLabel", label="Maya Version",
                        width=k.AE_TEXT_WIDTH)
        menu = pm.optionMenu("hostMenu", acc=True)
        button = pm.button("addButton", label="Add Plugin Entry", width=90)

        _form_layout(
            label,
            menu,
            button,
            pm.text(label="", width=30)
        )

        popup = pm.popupMenu(parent=label)
        pm.setParent(popup, menu=True)
        pm.menuItem(label="Detect Software")
        pm.menuItem(label="Add Plugin Entry")

        pm.setParent("..")  # out of form

        pm.columnLayout("pluginLayout", adj=True)

        pm.setParent("..")  # out of columnLayout

        populate_ui(node_attr)


def populate_ui(node_attr):
    """Reconfigure action buttons when node changes."""
    host_attr = pm.Attribute(node_attr)
    plugin_attr = host_attr.node().attr("pluginSoftware")
    widgets = _get_widgets()

    if not coredata.valid():
        for item in pm.optionMenu(widgets["host_menu"], q=True, itemListLong=True):
            pm.deleteUI(item)
        pm.setParent(widgets["host_menu"], menu=True)
        pm.menuItem(label="Not connected")

    # update popup menu items
    _configure_popup_menu(host_attr, plugin_attr, widgets)

    pm.optionMenu(widgets["host_menu"], edit=True, changeCommand=pm.Callback(
        _set_host_software_value, host_attr, plugin_attr, widgets))

    pm.button(widgets["add_button"], edit=True, command=pm.Callback(
        _add_plugin,  plugin_attr, "unknown"))

    # Update this UI if the attribute changes by some other means
    # For example: setAttr, or another instance of the attribute editor.
    _setup_script_jobs(host_attr, plugin_attr, widgets)

    pm.evalDeferred(pm.Callback(_ensure_connection,
                                host_attr, plugin_attr, widgets))


def _setup_script_jobs(host_attr, plugin_attr, widgets):

    menu = widgets["host_menu"]
    pm.scriptJob(
        attributeChange=(
            host_attr,
            pm.Callback(_sync_all_menus_to_attributes,
                        host_attr, plugin_attr,  widgets),
        ),
        parent=menu,
        replacePrevious=True
    )

    pm.scriptJob(
        attributeChange=(
            plugin_attr,
            pm.Callback(_sync_all_menus_to_attributes,
                        host_attr, plugin_attr,  widgets),
        ),
        parent=menu
    )


def _get_widgets(parent=None):
    if not parent:
        parent = pm.setParent(q=True)

    host_label = AEcommon.find_ui("hostLabel", parent)
    return {
        "host_layout": AEcommon.find_ui("hostLayout", parent),
        "plugin_layout": AEcommon.find_ui("pluginLayout", parent),
        "host_label": host_label,
        "host_menu": AEcommon.find_ui("hostMenu", parent),
        "add_button": AEcommon.find_ui("addButton", parent),
        "popup_menu":  pm.control(host_label, q=True, popupMenuArray=True)[0]
    }


def _ensure_connection(host_attr, plugin_attr, widgets):
    """Fetch list of sw from Conductor.

    Use cached data on the module if force is False"""

    software_data = coredata.data().get("software")
    if not coredata.valid():
        return

    AEcommon.ensure_populate_menu(
        widgets["host_menu"], software_data.supported_host_names())
    _sync_all_menus_to_attributes(host_attr, plugin_attr,  widgets)


def _configure_popup_menu(host_attr, plugin_attr, widgets):

    detect_item, add_plugin_item = pm.popupMenu(
        widgets["popup_menu"], q=True, itemArray=True)

    pm.menuItem(detect_item, edit=True, command=pm.Callback(
        _detect_software, host_attr, plugin_attr, widgets))

    pm.menuItem(add_plugin_item, edit=True, command=pm.Callback(
        _add_plugin,  plugin_attr, "unknown"))


def _detect_software(host_attr, plugin_attr, widgets):
    host_software_name = software.detect_host()
    host_attr.set(host_software_name)
    _remove_all_plugins(plugin_attr)
    for plugin_software_name in list(filter(None, [
        software.detect_mtoa(),
        software.detect_rfm(),
        software.detect_vray(),
        software.detect_redshift(),
        software.detect_yeti(),

    ])):
        _add_plugin(plugin_attr, plugin_software_name)


def _add_plugin(plugin_attr, plugin_name):
    AEcommon.next_available_element_plug(plugin_attr).set(plugin_name)


def _remove_all_plugins(plugin_attr):
    for index in plugin_attr.getArrayIndices():
        pm.removeMultiInstance(plugin_attr[index], b=True)


def _sync_all_menus_to_attributes(host_attr, plugin_attr,  widgets):

    AEcommon.sync_menu_to_attr(widgets["host_menu"], host_attr, default=-1)

    _sync_plugin_software_menus(
        host_attr, plugin_attr, widgets["plugin_layout"])


def _set_host_software_value(host_attr, plugin_attr, widgets):
    """
    Respond to host menu change.
    """

    num_items = pm.optionMenu(widgets["host_menu"], q=True, numberOfItems=True)
    if not num_items:
        return
    selected_value = pm.optionMenu(widgets["host_menu"], q=True, value=True)
    host_attr.set(selected_value)
    AEcommon.print_setAttr_cmd(host_attr)

    _sync_plugin_software_menus(
        host_attr, plugin_attr, widgets["plugin_layout"])


def _sync_plugin_software_menus(host_attr, plugin_attr, plugin_layout):
    """
     Make sure plugin menu items reflect the pluginSoftware attribute values.

     We simply delete all UI and rebuild from scratch.
    """

    for widget in (
        pm.layout(plugin_layout, q=True, childArray=True) or []
    ):
        pm.deleteUI(widget)

    if not plugin_attr.getArrayIndices():
        return

    software_data = coredata.data().get("software")
    supported_plugins = software_data.supported_plugins(host_attr.get())
    if not supported_plugins:
        return

    for element_attr in plugin_attr:
        if element_attr.get():
            pm.setParent(plugin_layout)

            _build_plugin_option_menus(element_attr, supported_plugins)


def _build_plugin_option_menus(attr, supported_plugins):
    """
    Build 2 menus (plugin, version) for the one plugin at index.

    The plugin at node.attr("pluginSoftware")[index] is something like:
    "vray 1.2.3" so we check that it is supported by the current maya
    version, and if not we reset the attr to one that is. Then we build the
    two menus.
    1. plugin menu contains all plugin names supported by current maya
        version.
    2. version menu contains versions of the currently selected plugin.
    """

    valid_plugin = _ensure_valid_selected_plugin(attr, supported_plugins)
    if not valid_plugin:
        return

    plugin, version = valid_plugin

    label = pm.text(label="Plugin Version", width=k.AE_TEXT_WIDTH)
    plugin_menu = pm.optionMenu(acc=True)
    version_menu = pm.optionMenu(acc=True)
    remove_btn = pm.symbolButton(
        image="smallTrash.xpm", ann="Remove plugin")

    form = _form_layout(
        label,
        plugin_menu,
        version_menu,
        remove_btn
    )

    pm.setParent(plugin_menu, menu=True)
    for p in supported_plugins:
        pm.menuItem(label=p["plugin"])

    pm.optionMenu(
        plugin_menu,
        edit=True,
        changeCommand=pm.Callback(
            _plugin_menu_change, attr, supported_plugins, plugin_menu, version_menu)
    )

    pm.optionMenu(
        version_menu,
        edit=True,
        changeCommand=pm.Callback(
            _version_menu_change, attr, plugin_menu, version_menu
        ),
    )
    pm.symbolButton(remove_btn, edit=True,
                    command=pm.Callback(_on_remove_plugin, attr))

    plugin_index = _get_plugin_index(plugin, supported_plugins)
    versions = _get_versions_for_supported_plugin(plugin, supported_plugins)
    pm.optionMenu(plugin_menu, edit=True, sl=(plugin_index+1))

    # now buildversion menu
    pm.setParent(version_menu, menu=True)
    for v in versions:
        pm.menuItem(label=v)

    version_index = _get_version_index(version, versions)
    pm.optionMenu(version_menu, edit=True, sl=(version_index+1))


def _ensure_valid_selected_plugin(attr, supported_plugins):
    if not supported_plugins:
        return
    current = attr.get()
    try:
        current_plugin, current_version = current.split(" ")
        found_plugin = next(
            (x for x in supported_plugins if x["plugin"] == current_plugin), None)
        if found_plugin:
            found_version = next(
                (x for x in found_plugin["versions"]
                 if x == current_version), None
            )
            if not found_version:
                current_version = found_plugin["versions"][-1]
        else:
            current_plugin = supported_plugins[0]["plugin"]
            current_version = supported_plugins[0]["versions"][-1]
    except (ValueError, AttributeError):
        current_plugin = supported_plugins[0]["plugin"]
        current_version = supported_plugins[0]["versions"][-1]
    current_plugin_value = "{} {}".format(current_plugin, current_version)
    if attr.get() != current_plugin_value:
        attr.set(current_plugin_value)
        AEcommon.print_setAttr_cmd(attr)

    return (current_plugin, current_version)


def _plugin_menu_change(attr, supported_plugins, plugin_menu, version_menu):
    """Callback when plugin menu item is selected.

    We rebuild the versions menu for this plugin, and select the last
    element.
    """
    plugin = pm.optionMenu(plugin_menu, q=True, value=True)
    versions = _get_versions_for_supported_plugin(plugin, supported_plugins)

    pm.setParent(version_menu, menu=True)
    for item in pm.optionMenu(version_menu, q=True, itemListLong=True):
        pm.deleteUI(item)
    for v in versions:
        pm.menuItem(label=v)
    pm.optionMenu(version_menu, edit=True, sl=len(versions))

    attr.set("{} {}".format(plugin, versions[-1]))
    AEcommon.print_setAttr_cmd(attr)


def _version_menu_change(attr, plugin_menu, version_menu):
    """Callback when version menu item is selected.

    Set the attribute to the string combination of 'plugin version'
    """
    plugin = pm.optionMenu(plugin_menu, q=True, value=True)
    version = pm.optionMenu(version_menu, q=True, value=True)
    value = "{} {}".format(plugin, version)
    if value != attr.get():
        attr.set(value)
        AEcommon.print_setAttr_cmd(attr)


def _on_remove_plugin(attr):
    """Remove attr multi element.
    Redraw is triggered automatically.
    """
    pm.removeMultiInstance(attr, b=True)


def _get_versions_for_supported_plugin(plugin, plugins):
    return next((x["versions"] for x in plugins if x["plugin"] == plugin), None)


def _get_plugin_index(plugin, plugins):
    return next((i for i, x in enumerate(plugins) if x["plugin"] == plugin), None)


def _get_version_index(version, versions):
    return next((i for i, x in enumerate(versions) if x == version), None)


def _form_layout(*widgets):
    # There must be 4 widgets.
    # we stretch the second and third widget.
    form = pm.formLayout(nd=100)
    for widget in widgets:
        pm.control(widget, edit=True, parent=form)

    form.attachForm(widgets[0], "left", 2)
    form.attachNone(widgets[0], "right")
    form.attachForm(widgets[0], "top", 2)
    form.attachForm(widgets[0], "bottom", 2)

    form.attachControl(widgets[1], "left", 2, widgets[0])
    form.attachPosition(widgets[1], "right", 2,  65)
    form.attachForm(widgets[1], "top", 2)
    form.attachForm(widgets[1], "bottom", 2)

    form.attachControl(widgets[2], "left", 2, widgets[1])
    form.attachControl(widgets[2], "right", 2, widgets[3])
    form.attachForm(widgets[2], "top", 2)
    form.attachForm(widgets[2], "bottom", 2)

    form.attachNone(widgets[3], "left")
    form.attachForm(widgets[3], "right", 2)
    form.attachForm(widgets[3], "top", 2)
    form.attachForm(widgets[3], "bottom", 2)

    return form
