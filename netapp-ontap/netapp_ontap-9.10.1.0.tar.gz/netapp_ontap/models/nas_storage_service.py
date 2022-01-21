r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NasStorageService", "NasStorageServiceSchema"]
__pdoc__ = {
    "NasStorageServiceSchema.resource": False,
    "NasStorageService": False,
}


class NasStorageServiceSchema(ResourceSchema):
    """The fields of the NasStorageService object"""

    name = fields.Str(data_key="name")
    r""" The storage service of the application component.

Valid choices:

* extreme
* performance
* value """

    @property
    def resource(self):
        return NasStorageService

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


class NasStorageService(Resource):

    _schema = NasStorageServiceSchema
