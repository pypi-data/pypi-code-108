r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VsiOnNasDatastore", "VsiOnNasDatastoreSchema"]
__pdoc__ = {
    "VsiOnNasDatastoreSchema.resource": False,
    "VsiOnNasDatastore": False,
}


class VsiOnNasDatastoreSchema(ResourceSchema):
    """The fields of the VsiOnNasDatastore object"""

    count = Size(data_key="count")
    r""" The number of datastores to support. """

    size = Size(data_key="size")
    r""" The size of the datastore. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    storage_service = fields.Nested("netapp_ontap.models.vsi_on_nas_datastore_storage_service.VsiOnNasDatastoreStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the vsi_on_nas_datastore. """

    @property
    def resource(self):
        return VsiOnNasDatastore

    gettable_fields = [
        "count",
        "size",
        "storage_service",
    ]
    """count,size,storage_service,"""

    patchable_fields = [
        "count",
        "storage_service",
    ]
    """count,storage_service,"""

    postable_fields = [
        "count",
        "size",
        "storage_service",
    ]
    """count,size,storage_service,"""


class VsiOnNasDatastore(Resource):

    _schema = VsiOnNasDatastoreSchema
