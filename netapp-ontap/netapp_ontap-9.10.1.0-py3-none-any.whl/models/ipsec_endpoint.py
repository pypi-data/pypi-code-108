r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IpsecEndpoint", "IpsecEndpointSchema"]
__pdoc__ = {
    "IpsecEndpointSchema.resource": False,
    "IpsecEndpoint": False,
}


class IpsecEndpointSchema(ResourceSchema):
    """The fields of the IpsecEndpoint object"""

    address = fields.Str(data_key="address")
    r""" The address field of the ipsec_endpoint. """

    family = fields.Str(data_key="family")
    r""" The family field of the ipsec_endpoint. """

    netmask = fields.Str(data_key="netmask")
    r""" The netmask field of the ipsec_endpoint. """

    port = fields.Str(data_key="port")
    r""" Application port to be covered by the IPsec policy

Example: 23 """

    @property
    def resource(self):
        return IpsecEndpoint

    gettable_fields = [
        "address",
        "family",
        "netmask",
        "port",
    ]
    """address,family,netmask,port,"""

    patchable_fields = [
        "address",
        "family",
        "netmask",
        "port",
    ]
    """address,family,netmask,port,"""

    postable_fields = [
        "address",
        "family",
        "netmask",
        "port",
    ]
    """address,family,netmask,port,"""


class IpsecEndpoint(Resource):

    _schema = IpsecEndpointSchema
