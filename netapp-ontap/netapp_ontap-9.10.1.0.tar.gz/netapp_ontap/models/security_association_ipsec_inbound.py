r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SecurityAssociationIpsecInbound", "SecurityAssociationIpsecInboundSchema"]
__pdoc__ = {
    "SecurityAssociationIpsecInboundSchema.resource": False,
    "SecurityAssociationIpsecInbound": False,
}


class SecurityAssociationIpsecInboundSchema(ResourceSchema):
    """The fields of the SecurityAssociationIpsecInbound object"""

    bytes = Size(data_key="bytes")
    r""" Number of inbound bytes for the IPsec security association. """

    packets = Size(data_key="packets")
    r""" Number of inbound packets for the IPsec security association. """

    security_parameter_index = fields.Str(data_key="security_parameter_index")
    r""" Inbound security parameter index for the IPSec security association. """

    @property
    def resource(self):
        return SecurityAssociationIpsecInbound

    gettable_fields = [
        "bytes",
        "packets",
        "security_parameter_index",
    ]
    """bytes,packets,security_parameter_index,"""

    patchable_fields = [
        "bytes",
        "packets",
        "security_parameter_index",
    ]
    """bytes,packets,security_parameter_index,"""

    postable_fields = [
        "bytes",
        "packets",
        "security_parameter_index",
    ]
    """bytes,packets,security_parameter_index,"""


class SecurityAssociationIpsecInbound(Resource):

    _schema = SecurityAssociationIpsecInboundSchema
