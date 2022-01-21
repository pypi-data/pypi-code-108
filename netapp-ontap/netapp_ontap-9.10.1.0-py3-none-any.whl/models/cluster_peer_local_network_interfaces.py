r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ClusterPeerLocalNetworkInterfaces", "ClusterPeerLocalNetworkInterfacesSchema"]
__pdoc__ = {
    "ClusterPeerLocalNetworkInterfacesSchema.resource": False,
    "ClusterPeerLocalNetworkInterfaces": False,
}


class ClusterPeerLocalNetworkInterfacesSchema(ResourceSchema):
    """The fields of the ClusterPeerLocalNetworkInterfaces object"""

    ip_address = fields.Str(data_key="ip_address")
    r""" List of local intercluster IP addresses. """

    @property
    def resource(self):
        return ClusterPeerLocalNetworkInterfaces

    gettable_fields = [
        "ip_address",
    ]
    """ip_address,"""

    patchable_fields = [
        "ip_address",
    ]
    """ip_address,"""

    postable_fields = [
        "ip_address",
    ]
    """ip_address,"""


class ClusterPeerLocalNetworkInterfaces(Resource):

    _schema = ClusterPeerLocalNetworkInterfacesSchema
