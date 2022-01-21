r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfAcps", "ShelfAcpsSchema"]
__pdoc__ = {
    "ShelfAcpsSchema.resource": False,
    "ShelfAcps": False,
}


class ShelfAcpsSchema(ResourceSchema):
    """The fields of the ShelfAcps object"""

    address = fields.Str(data_key="address")
    r""" The address field of the shelf_acps.

Example: 192.168.1.104 """

    channel = fields.Str(data_key="channel")
    r""" The channel field of the shelf_acps.

Valid choices:

* unknown
* out_of_band
* in_band """

    connection_state = fields.Str(data_key="connection_state")
    r""" The connection_state field of the shelf_acps.

Valid choices:

* no_connectivity
* partial_connectivity
* full_connectivity
* additional_connectivity
* unknown_connectivity
* not_available
* active
* disabled """

    enabled = fields.Boolean(data_key="enabled")
    r""" The enabled field of the shelf_acps. """

    error = fields.Nested("netapp_ontap.models.shelf_error.ShelfErrorSchema", unknown=EXCLUDE, data_key="error")
    r""" The error field of the shelf_acps. """

    netmask = fields.Str(data_key="netmask")
    r""" The netmask field of the shelf_acps.

Example: 255.255.252.0 """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the shelf_acps. """

    port = fields.Str(data_key="port")
    r""" The port field of the shelf_acps.

Example: e0P """

    subnet = fields.Str(data_key="subnet")
    r""" The subnet field of the shelf_acps.

Example: 192.168.0.1 """

    @property
    def resource(self):
        return ShelfAcps

    gettable_fields = [
        "address",
        "channel",
        "connection_state",
        "enabled",
        "error",
        "netmask",
        "node.links",
        "node.name",
        "node.uuid",
        "port",
        "subnet",
    ]
    """address,channel,connection_state,enabled,error,netmask,node.links,node.name,node.uuid,port,subnet,"""

    patchable_fields = [
        "address",
        "channel",
        "connection_state",
        "enabled",
        "error",
        "netmask",
        "node.name",
        "node.uuid",
        "port",
        "subnet",
    ]
    """address,channel,connection_state,enabled,error,netmask,node.name,node.uuid,port,subnet,"""

    postable_fields = [
        "address",
        "channel",
        "connection_state",
        "enabled",
        "error",
        "netmask",
        "node.name",
        "node.uuid",
        "port",
        "subnet",
    ]
    """address,channel,connection_state,enabled,error,netmask,node.name,node.uuid,port,subnet,"""


class ShelfAcps(Resource):

    _schema = ShelfAcpsSchema
