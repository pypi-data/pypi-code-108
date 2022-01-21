r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationSanAccessFcpEndpoint", "ApplicationSanAccessFcpEndpointSchema"]
__pdoc__ = {
    "ApplicationSanAccessFcpEndpointSchema.resource": False,
    "ApplicationSanAccessFcpEndpoint": False,
}


class ApplicationSanAccessFcpEndpointSchema(ResourceSchema):
    """The fields of the ApplicationSanAccessFcpEndpoint object"""

    interface = fields.Nested("netapp_ontap.resources.fc_interface.FcInterfaceSchema", unknown=EXCLUDE, data_key="interface")
    r""" The interface field of the application_san_access_fcp_endpoint. """

    @property
    def resource(self):
        return ApplicationSanAccessFcpEndpoint

    gettable_fields = [
        "interface.links",
        "interface.name",
        "interface.uuid",
        "interface.wwpn",
    ]
    """interface.links,interface.name,interface.uuid,interface.wwpn,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationSanAccessFcpEndpoint(Resource):

    _schema = ApplicationSanAccessFcpEndpointSchema
