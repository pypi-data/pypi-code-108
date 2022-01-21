r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationStatisticsStorageService", "ApplicationStatisticsStorageServiceSchema"]
__pdoc__ = {
    "ApplicationStatisticsStorageServiceSchema.resource": False,
    "ApplicationStatisticsStorageService": False,
}


class ApplicationStatisticsStorageServiceSchema(ResourceSchema):
    """The fields of the ApplicationStatisticsStorageService object"""

    name = fields.Str(data_key="name")
    r""" The storage service name. AFF systems support the extreme storage service. All other systems only support value. """

    uuid = fields.Str(data_key="uuid")
    r""" The storage service UUID. """

    @property
    def resource(self):
        return ApplicationStatisticsStorageService

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


class ApplicationStatisticsStorageService(Resource):

    _schema = ApplicationStatisticsStorageServiceSchema
