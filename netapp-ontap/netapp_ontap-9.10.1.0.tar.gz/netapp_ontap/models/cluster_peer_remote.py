r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ClusterPeerRemote", "ClusterPeerRemoteSchema"]
__pdoc__ = {
    "ClusterPeerRemoteSchema.resource": False,
    "ClusterPeerRemote": False,
}


class ClusterPeerRemoteSchema(ResourceSchema):
    """The fields of the ClusterPeerRemote object"""

    ip_addresses = fields.List(fields.Str, data_key="ip_addresses")
    r""" The IPv4 addresses, IPv6 addresses, or hostnames of the peers. """

    name = fields.Str(data_key="name")
    r""" The name of the remote cluster.

Example: cluster2 """

    serial_number = fields.Str(data_key="serial_number")
    r""" The serial number of the remote cluster.

Example: 4048820-60-9 """

    @property
    def resource(self):
        return ClusterPeerRemote

    gettable_fields = [
        "ip_addresses",
        "name",
        "serial_number",
    ]
    """ip_addresses,name,serial_number,"""

    patchable_fields = [
        "ip_addresses",
    ]
    """ip_addresses,"""

    postable_fields = [
        "ip_addresses",
    ]
    """ip_addresses,"""


class ClusterPeerRemote(Resource):

    _schema = ClusterPeerRemoteSchema
