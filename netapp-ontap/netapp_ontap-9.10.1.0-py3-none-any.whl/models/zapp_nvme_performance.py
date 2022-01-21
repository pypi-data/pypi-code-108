r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ZappNvmePerformance", "ZappNvmePerformanceSchema"]
__pdoc__ = {
    "ZappNvmePerformanceSchema.resource": False,
    "ZappNvmePerformance": False,
}


class ZappNvmePerformanceSchema(ResourceSchema):
    """The fields of the ZappNvmePerformance object"""

    storage_service = fields.Nested("netapp_ontap.models.nas_storage_service.NasStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the zapp_nvme_performance. """

    @property
    def resource(self):
        return ZappNvmePerformance

    gettable_fields = [
        "storage_service",
    ]
    """storage_service,"""

    patchable_fields = [
        "storage_service",
    ]
    """storage_service,"""

    postable_fields = [
        "storage_service",
    ]
    """storage_service,"""


class ZappNvmePerformance(Resource):

    _schema = ZappNvmePerformanceSchema
