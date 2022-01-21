r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FcInterfaceLocation", "FcInterfaceLocationSchema"]
__pdoc__ = {
    "FcInterfaceLocationSchema.resource": False,
    "FcInterfaceLocation": False,
}


class FcInterfaceLocationSchema(ResourceSchema):
    """The fields of the FcInterfaceLocation object"""

    home_node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="home_node")
    r""" The home_node field of the fc_interface_location. """

    home_port = fields.Nested("netapp_ontap.resources.fc_port.FcPortSchema", unknown=EXCLUDE, data_key="home_port")
    r""" The home_port field of the fc_interface_location. """

    is_home = fields.Boolean(data_key="is_home")
    r""" Indicates whether or not the FC interface currently resides on the home node. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the fc_interface_location. """

    port = fields.Nested("netapp_ontap.resources.fc_port.FcPortSchema", unknown=EXCLUDE, data_key="port")
    r""" The port field of the fc_interface_location. """

    @property
    def resource(self):
        return FcInterfaceLocation

    gettable_fields = [
        "home_node.links",
        "home_node.name",
        "home_node.uuid",
        "home_port.links",
        "home_port.name",
        "home_port.node",
        "home_port.uuid",
        "is_home",
        "node.links",
        "node.name",
        "node.uuid",
        "port.links",
        "port.name",
        "port.node",
        "port.uuid",
    ]
    """home_node.links,home_node.name,home_node.uuid,home_port.links,home_port.name,home_port.node,home_port.uuid,is_home,node.links,node.name,node.uuid,port.links,port.name,port.node,port.uuid,"""

    patchable_fields = [
        "home_node.name",
        "home_node.uuid",
        "home_port.name",
        "home_port.node",
        "home_port.uuid",
        "node.name",
        "node.uuid",
        "port.name",
        "port.node",
        "port.uuid",
    ]
    """home_node.name,home_node.uuid,home_port.name,home_port.node,home_port.uuid,node.name,node.uuid,port.name,port.node,port.uuid,"""

    postable_fields = [
        "home_node.name",
        "home_node.uuid",
        "home_port.name",
        "home_port.node",
        "home_port.uuid",
        "node.name",
        "node.uuid",
        "port.name",
        "port.node",
        "port.uuid",
    ]
    """home_node.name,home_node.uuid,home_port.name,home_port.node,home_port.uuid,node.name,node.uuid,port.name,port.node,port.uuid,"""


class FcInterfaceLocation(Resource):

    _schema = FcInterfaceLocationSchema
