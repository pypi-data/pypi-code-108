r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationNamespaceObject", "ApplicationNamespaceObjectSchema"]
__pdoc__ = {
    "ApplicationNamespaceObjectSchema.resource": False,
    "ApplicationNamespaceObject": False,
}


class ApplicationNamespaceObjectSchema(ResourceSchema):
    """The fields of the ApplicationNamespaceObject object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the application_namespace_object. """

    creation_timestamp = ImpreciseDateTime(data_key="creation_timestamp")
    r""" Namespace creation time """

    name = fields.Str(data_key="name")
    r""" Namespace name """

    size = Size(data_key="size")
    r""" Namespace size """

    uuid = fields.Str(data_key="uuid")
    r""" Namespace UUID """

    @property
    def resource(self):
        return ApplicationNamespaceObject

    gettable_fields = [
        "links",
        "creation_timestamp",
        "name",
        "size",
        "uuid",
    ]
    """links,creation_timestamp,name,size,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationNamespaceObject(Resource):

    _schema = ApplicationNamespaceObjectSchema
