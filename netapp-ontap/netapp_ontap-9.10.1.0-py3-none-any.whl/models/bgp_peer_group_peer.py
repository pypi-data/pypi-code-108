r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["BgpPeerGroupPeer", "BgpPeerGroupPeerSchema"]
__pdoc__ = {
    "BgpPeerGroupPeerSchema.resource": False,
    "BgpPeerGroupPeer": False,
}


class BgpPeerGroupPeerSchema(ResourceSchema):
    """The fields of the BgpPeerGroupPeer object"""

    address = fields.Str(data_key="address")
    r""" Peer router address

Example: 10.10.10.7 """

    asn = Size(data_key="asn")
    r""" Autonomous system number of peer """

    is_next_hop = fields.Boolean(data_key="is_next_hop")
    r""" Use peer address as next hop. """

    @property
    def resource(self):
        return BgpPeerGroupPeer

    gettable_fields = [
        "address",
        "asn",
        "is_next_hop",
    ]
    """address,asn,is_next_hop,"""

    patchable_fields = [
        "address",
        "is_next_hop",
    ]
    """address,is_next_hop,"""

    postable_fields = [
        "address",
        "asn",
        "is_next_hop",
    ]
    """address,asn,is_next_hop,"""


class BgpPeerGroupPeer(Resource):

    _schema = BgpPeerGroupPeerSchema
