r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IpInterfaceSvmIp", "IpInterfaceSvmIpSchema"]
__pdoc__ = {
    "IpInterfaceSvmIpSchema.resource": False,
    "IpInterfaceSvmIp": False,
}


class IpInterfaceSvmIpSchema(ResourceSchema):
    """The fields of the IpInterfaceSvmIp object"""

    address = fields.Str(data_key="address")
    r""" The address field of the ip_interface_svm_ip. """

    netmask = fields.Str(data_key="netmask")
    r""" The netmask field of the ip_interface_svm_ip. """

    @property
    def resource(self):
        return IpInterfaceSvmIp

    gettable_fields = [
        "address",
        "netmask",
    ]
    """address,netmask,"""

    patchable_fields = [
        "address",
        "netmask",
    ]
    """address,netmask,"""

    postable_fields = [
        "address",
        "netmask",
    ]
    """address,netmask,"""


class IpInterfaceSvmIp(Resource):

    _schema = IpInterfaceSvmIpSchema
