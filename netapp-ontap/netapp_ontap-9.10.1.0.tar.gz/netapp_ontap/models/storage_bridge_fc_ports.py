r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageBridgeFcPorts", "StorageBridgeFcPortsSchema"]
__pdoc__ = {
    "StorageBridgeFcPortsSchema.resource": False,
    "StorageBridgeFcPorts": False,
}


class StorageBridgeFcPortsSchema(ResourceSchema):
    """The fields of the StorageBridgeFcPorts object"""

    configured_data_rate = fields.Number(data_key="configured_data_rate")
    r""" Bridge FC port configured data rate, in Gbps """

    connection_mode = fields.Str(data_key="connection_mode")
    r""" Bridge FC port configured connection mode

Valid choices:

* loop
* ptp
* loop_preferred
* ptp_preferred """

    data_rate_capability = fields.Number(data_key="data_rate_capability")
    r""" Bridge FC port data rate capability, in Gbps """

    enabled = fields.Boolean(data_key="enabled")
    r""" Indicates whether the bridge FC port is enabled. """

    id = Size(data_key="id")
    r""" Bridge FC port index """

    negotiated_data_rate = fields.Number(data_key="negotiated_data_rate")
    r""" Bridge FC port negotiated data rate, in Gbps """

    peer_wwn = fields.Str(data_key="peer_wwn")
    r""" Bridge FC port peer port world wide name

Example: 200650eb1a238892 """

    sfp = fields.Nested("netapp_ontap.models.storage_bridge_sfp.StorageBridgeSfpSchema", unknown=EXCLUDE, data_key="sfp")
    r""" The sfp field of the storage_bridge_fc_ports. """

    state = fields.Str(data_key="state")
    r""" Bridge FC port state

Valid choices:

* error
* online
* offline """

    wwn = fields.Str(data_key="wwn")
    r""" Bridge FC port world wide name

Example: 2100001086a54100 """

    @property
    def resource(self):
        return StorageBridgeFcPorts

    gettable_fields = [
        "configured_data_rate",
        "connection_mode",
        "data_rate_capability",
        "enabled",
        "id",
        "negotiated_data_rate",
        "peer_wwn",
        "sfp",
        "state",
        "wwn",
    ]
    """configured_data_rate,connection_mode,data_rate_capability,enabled,id,negotiated_data_rate,peer_wwn,sfp,state,wwn,"""

    patchable_fields = [
        "configured_data_rate",
        "connection_mode",
        "data_rate_capability",
        "enabled",
        "id",
        "negotiated_data_rate",
        "peer_wwn",
        "sfp",
        "state",
        "wwn",
    ]
    """configured_data_rate,connection_mode,data_rate_capability,enabled,id,negotiated_data_rate,peer_wwn,sfp,state,wwn,"""

    postable_fields = [
        "configured_data_rate",
        "connection_mode",
        "data_rate_capability",
        "enabled",
        "id",
        "negotiated_data_rate",
        "peer_wwn",
        "sfp",
        "state",
        "wwn",
    ]
    """configured_data_rate,connection_mode,data_rate_capability,enabled,id,negotiated_data_rate,peer_wwn,sfp,state,wwn,"""


class StorageBridgeFcPorts(Resource):

    _schema = StorageBridgeFcPortsSchema
