r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationSanAccessBackingStorage", "ApplicationSanAccessBackingStorageSchema"]
__pdoc__ = {
    "ApplicationSanAccessBackingStorageSchema.resource": False,
    "ApplicationSanAccessBackingStorage": False,
}


class ApplicationSanAccessBackingStorageSchema(ResourceSchema):
    """The fields of the ApplicationSanAccessBackingStorage object"""

    type = fields.Str(data_key="type")
    r""" Backing storage type

Valid choices:

* lun """

    uuid = fields.Str(data_key="uuid")
    r""" Backing storage UUID """

    @property
    def resource(self):
        return ApplicationSanAccessBackingStorage

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


class ApplicationSanAccessBackingStorage(Resource):

    _schema = ApplicationSanAccessBackingStorageSchema
