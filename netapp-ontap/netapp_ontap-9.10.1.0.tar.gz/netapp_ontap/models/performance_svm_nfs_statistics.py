r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["PerformanceSvmNfsStatistics", "PerformanceSvmNfsStatisticsSchema"]
__pdoc__ = {
    "PerformanceSvmNfsStatisticsSchema.resource": False,
    "PerformanceSvmNfsStatistics": False,
}


class PerformanceSvmNfsStatisticsSchema(ResourceSchema):
    """The fields of the PerformanceSvmNfsStatistics object"""

    v3 = fields.Nested("netapp_ontap.models.performance_metric_raw_svm.PerformanceMetricRawSvmSchema", unknown=EXCLUDE, data_key="v3")
    r""" The v3 field of the performance_svm_nfs_statistics. """

    v4 = fields.Nested("netapp_ontap.models.performance_metric_raw_svm.PerformanceMetricRawSvmSchema", unknown=EXCLUDE, data_key="v4")
    r""" The v4 field of the performance_svm_nfs_statistics. """

    v41 = fields.Nested("netapp_ontap.models.performance_metric_raw_svm.PerformanceMetricRawSvmSchema", unknown=EXCLUDE, data_key="v41")
    r""" The v41 field of the performance_svm_nfs_statistics. """

    @property
    def resource(self):
        return PerformanceSvmNfsStatistics

    gettable_fields = [
        "v3.iops_raw",
        "v3.latency_raw",
        "v3.status",
        "v3.throughput_raw",
        "v3.timestamp",
        "v4.iops_raw",
        "v4.latency_raw",
        "v4.status",
        "v4.throughput_raw",
        "v4.timestamp",
        "v41.iops_raw",
        "v41.latency_raw",
        "v41.status",
        "v41.throughput_raw",
        "v41.timestamp",
    ]
    """v3.iops_raw,v3.latency_raw,v3.status,v3.throughput_raw,v3.timestamp,v4.iops_raw,v4.latency_raw,v4.status,v4.throughput_raw,v4.timestamp,v41.iops_raw,v41.latency_raw,v41.status,v41.throughput_raw,v41.timestamp,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class PerformanceSvmNfsStatistics(Resource):

    _schema = PerformanceSvmNfsStatisticsSchema
