r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MaxdataOnSanApplicationComponentsStorageService", "MaxdataOnSanApplicationComponentsStorageServiceSchema"]
__pdoc__ = {
    "MaxdataOnSanApplicationComponentsStorageServiceSchema.resource": False,
    "MaxdataOnSanApplicationComponentsStorageService": False,
}


class MaxdataOnSanApplicationComponentsStorageServiceSchema(ResourceSchema):
    """The fields of the MaxdataOnSanApplicationComponentsStorageService object"""

    name = fields.Str(data_key="name")
    r""" The storage service of the application component.

Valid choices:

* extreme
* maxdata
* performance
* value """

    @property
    def resource(self):
        return MaxdataOnSanApplicationComponentsStorageService

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


class MaxdataOnSanApplicationComponentsStorageService(Resource):

    _schema = MaxdataOnSanApplicationComponentsStorageServiceSchema
