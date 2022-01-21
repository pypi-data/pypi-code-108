r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationSanAccessIscsiEndpoint", "ApplicationSanAccessIscsiEndpointSchema"]
__pdoc__ = {
    "ApplicationSanAccessIscsiEndpointSchema.resource": False,
    "ApplicationSanAccessIscsiEndpoint": False,
}


class ApplicationSanAccessIscsiEndpointSchema(ResourceSchema):
    """The fields of the ApplicationSanAccessIscsiEndpoint object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the application_san_access_iscsi_endpoint. """

    interface = fields.Nested("netapp_ontap.resources.ip_interface.IpInterfaceSchema", unknown=EXCLUDE, data_key="interface")
    r""" The interface field of the application_san_access_iscsi_endpoint. """

    port = Size(data_key="port")
    r""" The TCP port number of the iSCSI access endpoint.

Example: 3260 """

    @property
    def resource(self):
        return ApplicationSanAccessIscsiEndpoint

    gettable_fields = [
        "links",
        "interface.links",
        "interface.ip",
        "interface.name",
        "interface.uuid",
        "port",
    ]
    """links,interface.links,interface.ip,interface.name,interface.uuid,port,"""

    patchable_fields = [
        "interface.ip",
        "interface.name",
        "interface.uuid",
    ]
    """interface.ip,interface.name,interface.uuid,"""

    postable_fields = [
        "interface.ip",
        "interface.name",
        "interface.uuid",
    ]
    """interface.ip,interface.name,interface.uuid,"""


class ApplicationSanAccessIscsiEndpoint(Resource):

    _schema = ApplicationSanAccessIscsiEndpointSchema
