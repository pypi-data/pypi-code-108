r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IscsiConnectionInterface", "IscsiConnectionInterfaceSchema"]
__pdoc__ = {
    "IscsiConnectionInterfaceSchema.resource": False,
    "IscsiConnectionInterface": False,
}


class IscsiConnectionInterfaceSchema(ResourceSchema):
    """The fields of the IscsiConnectionInterface object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the iscsi_connection_interface. """

    ip = fields.Nested("netapp_ontap.models.iscsi_connection_interface_ip.IscsiConnectionInterfaceIpSchema", unknown=EXCLUDE, data_key="ip")
    r""" The ip field of the iscsi_connection_interface. """

    name = fields.Str(data_key="name")
    r""" The name of the interface.

Example: lif1 """

    uuid = fields.Str(data_key="uuid")
    r""" The UUID that uniquely identifies the interface.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return IscsiConnectionInterface

    gettable_fields = [
        "links",
        "ip",
        "name",
        "uuid",
    ]
    """links,ip,name,uuid,"""

    patchable_fields = [
        "ip",
    ]
    """ip,"""

    postable_fields = [
        "ip",
    ]
    """ip,"""


class IscsiConnectionInterface(Resource):

    _schema = IscsiConnectionInterfaceSchema
