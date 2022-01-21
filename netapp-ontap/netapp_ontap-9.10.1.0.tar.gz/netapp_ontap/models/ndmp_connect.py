r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NdmpConnect", "NdmpConnectSchema"]
__pdoc__ = {
    "NdmpConnectSchema.resource": False,
    "NdmpConnect": False,
}


class NdmpConnectSchema(ResourceSchema):
    """The fields of the NdmpConnect object"""

    address = fields.Str(data_key="address")
    r""" Indicates the NDMP data connection address. """

    port = Size(data_key="port")
    r""" Indicates the NDMP data connection port.

Example: 18600 """

    type = fields.Str(data_key="type")
    r""" Indicates the NDMP data connection type. """

    @property
    def resource(self):
        return NdmpConnect

    gettable_fields = [
        "address",
        "port",
        "type",
    ]
    """address,port,type,"""

    patchable_fields = [
        "address",
        "port",
        "type",
    ]
    """address,port,type,"""

    postable_fields = [
        "address",
        "port",
        "type",
    ]
    """address,port,type,"""


class NdmpConnect(Resource):

    _schema = NdmpConnectSchema
