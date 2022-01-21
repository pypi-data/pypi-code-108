r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeClusterInterface", "NodeClusterInterfaceSchema"]
__pdoc__ = {
    "NodeClusterInterfaceSchema.resource": False,
    "NodeClusterInterface": False,
}


class NodeClusterInterfaceSchema(ResourceSchema):
    """The fields of the NodeClusterInterface object"""

    ip = fields.Nested("netapp_ontap.models.node_setup_ip.NodeSetupIpSchema", unknown=EXCLUDE, data_key="ip")
    r""" The ip field of the node_cluster_interface. """

    @property
    def resource(self):
        return NodeClusterInterface

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


class NodeClusterInterface(Resource):

    _schema = NodeClusterInterfaceSchema
