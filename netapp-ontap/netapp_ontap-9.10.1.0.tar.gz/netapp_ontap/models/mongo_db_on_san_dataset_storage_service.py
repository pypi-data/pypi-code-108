r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MongoDbOnSanDatasetStorageService", "MongoDbOnSanDatasetStorageServiceSchema"]
__pdoc__ = {
    "MongoDbOnSanDatasetStorageServiceSchema.resource": False,
    "MongoDbOnSanDatasetStorageService": False,
}


class MongoDbOnSanDatasetStorageServiceSchema(ResourceSchema):
    """The fields of the MongoDbOnSanDatasetStorageService object"""

    name = fields.Str(data_key="name")
    r""" The storage service of the database.

Valid choices:

* extreme
* performance
* value """

    @property
    def resource(self):
        return MongoDbOnSanDatasetStorageService

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


class MongoDbOnSanDatasetStorageService(Resource):

    _schema = MongoDbOnSanDatasetStorageServiceSchema
