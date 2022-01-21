r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Ipv6InterfaceAndGateway", "Ipv6InterfaceAndGatewaySchema"]
__pdoc__ = {
    "Ipv6InterfaceAndGatewaySchema.resource": False,
    "Ipv6InterfaceAndGateway": False,
}


class Ipv6InterfaceAndGatewaySchema(ResourceSchema):
    """The fields of the Ipv6InterfaceAndGateway object"""

    address = fields.Str(data_key="address")
    r""" IPv6 address

Example: fd20:8b1e:b255:5011:10:141:4:97 """

    gateway = fields.Str(data_key="gateway")
    r""" The IPv6 address of the default router.

Example: fd20:8b1e:b255:5011:10::1 """

    netmask = Size(data_key="netmask")
    r""" The IPv6 netmask/prefix length. The default value is 64 with a valid range of 1 to 127.

Example: 64 """

    @property
    def resource(self):
        return Ipv6InterfaceAndGateway

    gettable_fields = [
        "address",
        "gateway",
        "netmask",
    ]
    """address,gateway,netmask,"""

    patchable_fields = [
        "address",
        "gateway",
        "netmask",
    ]
    """address,gateway,netmask,"""

    postable_fields = [
        "address",
        "gateway",
        "netmask",
    ]
    """address,gateway,netmask,"""


class Ipv6InterfaceAndGateway(Resource):

    _schema = Ipv6InterfaceAndGatewaySchema
