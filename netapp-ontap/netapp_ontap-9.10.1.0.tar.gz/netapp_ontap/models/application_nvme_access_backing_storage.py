r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationNvmeAccessBackingStorage", "ApplicationNvmeAccessBackingStorageSchema"]
__pdoc__ = {
    "ApplicationNvmeAccessBackingStorageSchema.resource": False,
    "ApplicationNvmeAccessBackingStorage": False,
}


class ApplicationNvmeAccessBackingStorageSchema(ResourceSchema):
    """The fields of the ApplicationNvmeAccessBackingStorage object"""

    type = fields.Str(data_key="type")
    r""" Backing storage type

Valid choices:

* namespace """

    uuid = fields.Str(data_key="uuid")
    r""" Backing storage UUID """

    @property
    def resource(self):
        return ApplicationNvmeAccessBackingStorage

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


class ApplicationNvmeAccessBackingStorage(Resource):

    _schema = ApplicationNvmeAccessBackingStorageSchema
