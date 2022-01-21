r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IpInterfaceReferenceIp", "IpInterfaceReferenceIpSchema"]
__pdoc__ = {
    "IpInterfaceReferenceIpSchema.resource": False,
    "IpInterfaceReferenceIp": False,
}


class IpInterfaceReferenceIpSchema(ResourceSchema):
    """The fields of the IpInterfaceReferenceIp object"""

    address = fields.Str(data_key="address")
    r""" The address field of the ip_interface_reference_ip. """

    @property
    def resource(self):
        return IpInterfaceReferenceIp

    gettable_fields = [
        "address",
    ]
    """address,"""

    patchable_fields = [
        "address",
    ]
    """address,"""

    postable_fields = [
        "address",
    ]
    """address,"""


class IpInterfaceReferenceIp(Resource):

    _schema = IpInterfaceReferenceIpSchema
