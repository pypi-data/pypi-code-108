r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationComponentStorageService", "ApplicationComponentStorageServiceSchema"]
__pdoc__ = {
    "ApplicationComponentStorageServiceSchema.resource": False,
    "ApplicationComponentStorageService": False,
}


class ApplicationComponentStorageServiceSchema(ResourceSchema):
    """The fields of the ApplicationComponentStorageService object"""

    name = fields.Str(data_key="name")
    r""" Storage service name """

    uuid = fields.Str(data_key="uuid")
    r""" Storage service UUID """

    @property
    def resource(self):
        return ApplicationComponentStorageService

    gettable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationComponentStorageService(Resource):

    _schema = ApplicationComponentStorageServiceSchema
