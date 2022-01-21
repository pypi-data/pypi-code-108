r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NfsServiceTransport", "NfsServiceTransportSchema"]
__pdoc__ = {
    "NfsServiceTransportSchema.resource": False,
    "NfsServiceTransport": False,
}


class NfsServiceTransportSchema(ResourceSchema):
    """The fields of the NfsServiceTransport object"""

    tcp_enabled = fields.Boolean(data_key="tcp_enabled")
    r""" Specifies whether TCP transports are enabled on the server. """

    udp_enabled = fields.Boolean(data_key="udp_enabled")
    r""" Specifies whether UDP transports are enabled on the server. """

    @property
    def resource(self):
        return NfsServiceTransport

    gettable_fields = [
        "tcp_enabled",
        "udp_enabled",
    ]
    """tcp_enabled,udp_enabled,"""

    patchable_fields = [
        "tcp_enabled",
        "udp_enabled",
    ]
    """tcp_enabled,udp_enabled,"""

    postable_fields = [
        "tcp_enabled",
        "udp_enabled",
    ]
    """tcp_enabled,udp_enabled,"""


class NfsServiceTransport(Resource):

    _schema = NfsServiceTransportSchema
