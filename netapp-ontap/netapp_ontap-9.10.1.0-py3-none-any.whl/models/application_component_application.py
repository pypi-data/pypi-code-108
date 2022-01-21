r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationComponentApplication", "ApplicationComponentApplicationSchema"]
__pdoc__ = {
    "ApplicationComponentApplicationSchema.resource": False,
    "ApplicationComponentApplication": False,
}


class ApplicationComponentApplicationSchema(ResourceSchema):
    """The fields of the ApplicationComponentApplication object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the application_component_application. """

    name = fields.Str(data_key="name")
    r""" Application name """

    uuid = fields.Str(data_key="uuid")
    r""" The application UUID. Valid in URL. """

    @property
    def resource(self):
        return ApplicationComponentApplication

    gettable_fields = [
        "links",
        "name",
        "uuid",
    ]
    """links,name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationComponentApplication(Resource):

    _schema = ApplicationComponentApplicationSchema
