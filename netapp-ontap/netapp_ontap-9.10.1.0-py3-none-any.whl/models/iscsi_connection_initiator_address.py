r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IscsiConnectionInitiatorAddress", "IscsiConnectionInitiatorAddressSchema"]
__pdoc__ = {
    "IscsiConnectionInitiatorAddressSchema.resource": False,
    "IscsiConnectionInitiatorAddress": False,
}


class IscsiConnectionInitiatorAddressSchema(ResourceSchema):
    """The fields of the IscsiConnectionInitiatorAddress object"""

    address = fields.Str(data_key="address")
    r""" The TCP IPv4 or IPv6 address of the initiator end of the iSCSI connection.


Example: 10.10.10.7 """

    port = Size(data_key="port")
    r""" The TCP port number of the initiator end of the iSCSI connection.


Example: 55432 """

    @property
    def resource(self):
        return IscsiConnectionInitiatorAddress

    gettable_fields = [
        "address",
        "port",
    ]
    """address,port,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class IscsiConnectionInitiatorAddress(Resource):

    _schema = IscsiConnectionInitiatorAddressSchema
