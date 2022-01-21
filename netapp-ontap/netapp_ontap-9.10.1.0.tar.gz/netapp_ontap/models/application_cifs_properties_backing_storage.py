r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationCifsPropertiesBackingStorage", "ApplicationCifsPropertiesBackingStorageSchema"]
__pdoc__ = {
    "ApplicationCifsPropertiesBackingStorageSchema.resource": False,
    "ApplicationCifsPropertiesBackingStorage": False,
}


class ApplicationCifsPropertiesBackingStorageSchema(ResourceSchema):
    """The fields of the ApplicationCifsPropertiesBackingStorage object"""

    type = fields.Str(data_key="type")
    r""" Backing storage type

Valid choices:

* volume """

    uuid = fields.Str(data_key="uuid")
    r""" Backing storage UUID """

    @property
    def resource(self):
        return ApplicationCifsPropertiesBackingStorage

    gettable_fields = [
        "type",
        "uuid",
    ]
    """type,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationCifsPropertiesBackingStorage(Resource):

    _schema = ApplicationCifsPropertiesBackingStorageSchema
