r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["PerformanceSvm", "PerformanceSvmSchema"]
__pdoc__ = {
    "PerformanceSvmSchema.resource": False,
    "PerformanceSvm": False,
}


class PerformanceSvmSchema(ResourceSchema):
    """The fields of the PerformanceSvm object"""

    links = fields.Nested("netapp_ontap.models.collection_links.CollectionLinksSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the performance_svm. """

    num_records = Size(data_key="num_records")
    r""" Number of records """

    records = fields.List(fields.Nested("netapp_ontap.models.performance_metric_svm.PerformanceMetricSvmSchema", unknown=EXCLUDE), data_key="records")
    r""" The records field of the performance_svm. """

    @property
    def resource(self):
        return PerformanceSvm

    gettable_fields = [
        "links",
        "num_records",
        "records.links",
        "records.duration",
        "records.iops",
        "records.latency",
        "records.status",
        "records.throughput",
        "records.timestamp",
    ]
    """links,num_records,records.links,records.duration,records.iops,records.latency,records.status,records.throughput,records.timestamp,"""

    patchable_fields = [
        "num_records",
        "records.iops",
        "records.latency",
        "records.throughput",
    ]
    """num_records,records.iops,records.latency,records.throughput,"""

    postable_fields = [
        "num_records",
        "records.iops",
        "records.latency",
        "records.throughput",
    ]
    """num_records,records.iops,records.latency,records.throughput,"""


class PerformanceSvm(Resource):

    _schema = PerformanceSvmSchema
