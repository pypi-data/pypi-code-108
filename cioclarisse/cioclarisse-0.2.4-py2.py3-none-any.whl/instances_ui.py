"""
Responds to events in the machines section of the ConductorJob attribute editor.

NOTE: In a future version we will also save the name of the instance type. This
    is because the value is numeric, but the menu is built dynamically from the
    list of instance types. So by stashing the name we can try to repair it if
    the list changes order between sessions.

"""
from ciocore import data as coredata
from cioclarisse import const as k

def update(obj):
    """
    Rebuilds the instance types menu. 

    Args:
        obj (ConductorJob): Item on which to rebuild menu.
    """

    instance_type_att = obj.get_attribute("instance_type")
    instance_type_att.remove_all_presets()

    if not coredata.valid():
        instance_type_att.add_preset(k.NOT_CONNECTED,  "0")
        return

    instance_types = coredata.data().get("instance_types")
    for i, instance_type in enumerate(instance_types):
        instance_type_att.add_preset(
            instance_type["description"].encode("utf-8"),  str(i))
