from contextlib import contextmanager
import pymel.core as pm


def print_setAttr_cmd(attr):
    try:
        attr = pm.Attribute(attr)
        if attr.type() == "string":
            pm.displayInfo('setAttr -type "string" "{}" "{}";'.format(
                attr.name(), attr.get()))
        else:
            pm.displayInfo('setAttr "{}" {};'.format(attr.name(), attr.get()))
    except BaseException:
        pass

@contextmanager
def ae_template():
    pm.setUITemplate("attributeEditorTemplate", pushTemplate=True)
    yield
    pm.setUITemplate(ppt=True)



def ensure_populate_menu(menu, values):
    items = pm.optionMenu(menu, q=True, itemListLong=True)
    labels = [pm.menuItem(i, q=True, label=True) for i in items]

    if labels == values:
        return
    for item in items:
        pm.deleteUI(item)
    pm.setParent(menu, menu=True)
    for value in values:
        pm.menuItem(label=value)


def next_available_element_plug(array_plug):

    indices = array_plug.getArrayIndices()
    next_available = next(a for a, b in enumerate(indices + [-1]) if a != b)
    return array_plug[next_available]


def sync_menu_to_attr(menu, attr, **kw):
    """
    Make sure menu item reflects the attribute value.

    If the attribute is invalid, set it to the default.

    kw[value_label_pairs] is a map of corresponence from  attribute values to
    menu labels. Example:

    [
        ("n2-standard-16", "2 core, 16 Gb Ram"),
        ("n8-standard-64", "8 core, 64 Gb Ram")
    ]

    default is the index of the  value/menu-item to use in case the attribute
    value is not in the available list.
    """

    default = kw.get("default", 0)
    items = pm.optionMenu(menu, q=True, itemListLong=True)
    if not items:
        return
    value = attr.get()

    # negative index means count value back from the end.
    # TODO find a more compact way to validate
    if default < 0:
        default = len(items) + default
    if default < 0:
        default = 0

    values = kw.get("values", [pm.menuItem(item, q=True, label=True) for item in items])

    if len(values) != len(items):
        raise ValueError(
            "Values were provided but do not match the number of menu items {}/{}.".format( len(values),len(items)))
 
    try:
        index = values.index(value)
    except ValueError:
        if kw.get("immutable"):
            raise ValueError("Value {} not found in menu".format(value))
        index = default
        attr.set(values[index])
        pm.displayInfo("{} is not available. Switching to {}. ".format(
            value, values[index]))
        print_setAttr_cmd(attr)

    pm.optionMenu(menu, edit=True, sl=(index + 1))




def find_ui(name, root=None):
    """""breadth first search for element by name under root."""
    if not root:
        root = pm.setParent(q=True)
    stack = [root]
    while stack:
        if stack[0].rpartition("|")[2] == name:
            return stack[0]
        if pm.layout(stack[0], q=True, exists=True):
            for child_ui in pm.layout(stack[0], q=True, childArray=True) or[]:
                 #must ensure short name because we build full path manually
                child_ui = child_ui.rpartition("|")[2]
                stack.append("{}|{}".format(stack[0],child_ui))

        stack = stack[1:]



def find_layout(parent, layout_name):
    return [p for p in pm.layout(parent, q=True, childArray=True) if p.rpartition(
        "|")[2] == layout_name][0]
