r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SecurityAssociationIpsecOutbound", "SecurityAssociationIpsecOutboundSchema"]
__pdoc__ = {
    "SecurityAssociationIpsecOutboundSchema.resource": False,
    "SecurityAssociationIpsecOutbound": False,
}


class SecurityAssociationIpsecOutboundSchema(ResourceSchema):
    """The fields of the SecurityAssociationIpsecOutbound object"""

    bytes = Size(data_key="bytes")
    r""" Number of outbound bytes for the IPsec security association. """

    packets = Size(data_key="packets")
    r""" Number of outbound packets for the IPsec security association. """

    security_parameter_index = fields.Str(data_key="security_parameter_index")
    r""" Outbound security parameter index for the IPSec security association. """

    @property
    def resource(self):
        return SecurityAssociationIpsecOutbound

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


class SecurityAssociationIpsecOutbound(Resource):

    _schema = SecurityAssociationIpsecOutboundSchema
