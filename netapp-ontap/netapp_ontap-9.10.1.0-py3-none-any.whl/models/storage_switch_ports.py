r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageSwitchPorts", "StorageSwitchPortsSchema"]
__pdoc__ = {
    "StorageSwitchPortsSchema.resource": False,
    "StorageSwitchPorts": False,
}


class StorageSwitchPortsSchema(ResourceSchema):
    """The fields of the StorageSwitchPorts object"""

    enabled = fields.Boolean(data_key="enabled")
    r""" Indicates whether the storage switch port is enabled. """

    mode = fields.Str(data_key="mode")
    r""" Storage switch port mode

Valid choices:

* unknown
* auto
* f_port
* fl_port
* e_port
* te_port
* u_port
* g_port
* other
* ex_port
* d_port
* sim_port
* ve_port
* ae_port
* af_port """

    name = fields.Str(data_key="name")
    r""" Storage switch port name """

    sfp = fields.Nested("netapp_ontap.models.storage_switch_sfp.StorageSwitchSfpSchema", unknown=EXCLUDE, data_key="sfp")
    r""" The sfp field of the storage_switch_ports. """

    speed = Size(data_key="speed")
    r""" Storage switch port speed, in Gbps """

    state = fields.Str(data_key="state")
    r""" Storage switch port state

Valid choices:

* error
* online
* offline """

    wwn = fields.Str(data_key="wwn")
    r""" Storage switch port world wide name """

    @property
    def resource(self):
        return StorageSwitchPorts

    gettable_fields = [
        "enabled",
        "mode",
        "name",
        "sfp",
        "speed",
        "state",
        "wwn",
    ]
    """enabled,mode,name,sfp,speed,state,wwn,"""

    patchable_fields = [
        "enabled",
        "mode",
        "name",
        "sfp",
        "speed",
        "state",
        "wwn",
    ]
    """enabled,mode,name,sfp,speed,state,wwn,"""

    postable_fields = [
        "enabled",
        "mode",
        "name",
        "sfp",
        "speed",
        "state",
        "wwn",
    ]
    """enabled,mode,name,sfp,speed,state,wwn,"""


class StorageSwitchPorts(Resource):

    _schema = StorageSwitchPortsSchema
