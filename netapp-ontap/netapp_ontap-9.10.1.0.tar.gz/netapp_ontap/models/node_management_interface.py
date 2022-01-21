r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeManagementInterface", "NodeManagementInterfaceSchema"]
__pdoc__ = {
    "NodeManagementInterfaceSchema.resource": False,
    "NodeManagementInterface": False,
}


class NodeManagementInterfaceSchema(ResourceSchema):
    """The fields of the NodeManagementInterface object"""

    ip = fields.Nested("netapp_ontap.models.node_setup_ip.NodeSetupIpSchema", unknown=EXCLUDE, data_key="ip")
    r""" The ip field of the node_management_interface. """

    @property
    def resource(self):
        return NodeManagementInterface

    gettable_fields = [
    ]
    """"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "ip",
    ]
    """ip,"""


class NodeManagementInterface(Resource):

    _schema = NodeManagementInterfaceSchema
