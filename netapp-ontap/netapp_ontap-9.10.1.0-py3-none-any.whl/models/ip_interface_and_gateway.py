r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IpInterfaceAndGateway", "IpInterfaceAndGatewaySchema"]
__pdoc__ = {
    "IpInterfaceAndGatewaySchema.resource": False,
    "IpInterfaceAndGateway": False,
}


class IpInterfaceAndGatewaySchema(ResourceSchema):
    """The fields of the IpInterfaceAndGateway object"""

    address = fields.Str(data_key="address")
    r""" IPv4 or IPv6 address

Example: 10.10.10.7 """

    gateway = fields.Str(data_key="gateway")
    r""" The IPv4 or IPv6 address of the default router.

Example: 10.1.1.1 """

    netmask = fields.Str(data_key="netmask")
    r""" The netmask field of the ip_interface_and_gateway. """

    @property
    def resource(self):
        return IpInterfaceAndGateway

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


class IpInterfaceAndGateway(Resource):

    _schema = IpInterfaceAndGatewaySchema
