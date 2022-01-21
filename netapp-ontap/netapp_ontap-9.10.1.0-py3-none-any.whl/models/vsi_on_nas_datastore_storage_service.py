r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VsiOnNasDatastoreStorageService", "VsiOnNasDatastoreStorageServiceSchema"]
__pdoc__ = {
    "VsiOnNasDatastoreStorageServiceSchema.resource": False,
    "VsiOnNasDatastoreStorageService": False,
}


class VsiOnNasDatastoreStorageServiceSchema(ResourceSchema):
    """The fields of the VsiOnNasDatastoreStorageService object"""

    name = fields.Str(data_key="name")
    r""" The storage service of the datastore.

Valid choices:

* extreme
* performance
* value """

    @property
    def resource(self):
        return VsiOnNasDatastoreStorageService

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class VsiOnNasDatastoreStorageService(Resource):

    _schema = VsiOnNasDatastoreStorageServiceSchema
