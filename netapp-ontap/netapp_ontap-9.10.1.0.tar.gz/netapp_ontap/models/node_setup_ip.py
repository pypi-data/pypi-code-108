r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeSetupIp", "NodeSetupIpSchema"]
__pdoc__ = {
    "NodeSetupIpSchema.resource": False,
    "NodeSetupIp": False,
}


class NodeSetupIpSchema(ResourceSchema):
    """The fields of the NodeSetupIp object"""

    address = fields.Str(data_key="address")
    r""" The address field of the node_setup_ip. """

    @property
    def resource(self):
        return NodeSetupIp

    gettable_fields = [
    ]
    """"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "address",
    ]
    """address,"""


class NodeSetupIp(Resource):

    _schema = NodeSetupIpSchema
