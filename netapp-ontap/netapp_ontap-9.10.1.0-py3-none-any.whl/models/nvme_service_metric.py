r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NvmeServiceMetric", "NvmeServiceMetricSchema"]
__pdoc__ = {
    "NvmeServiceMetricSchema.resource": False,
    "NvmeServiceMetric": False,
}


class NvmeServiceMetricSchema(ResourceSchema):
    """The fields of the NvmeServiceMetric object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the nvme_service_metric. """

    duration = fields.Str(data_key="duration")
    r""" The duration over which this sample is calculated. The time durations are represented in the ISO-8601 standard format. Samples can be calculated over the following durations:


Valid choices:

* PT15S
* PT4M
* PT30M
* PT2H
* P1D
* PT5M """

    fc = fields.Nested("netapp_ontap.models.performance_metric_svm.PerformanceMetricSvmSchema", unknown=EXCLUDE, data_key="fc")
    r""" The fc field of the nvme_service_metric. """

    iops = fields.Nested("netapp_ontap.models.performance_metric_io_type.PerformanceMetricIoTypeSchema", unknown=EXCLUDE, data_key="iops")
    r""" The iops field of the nvme_service_metric. """

    latency = fields.Nested("netapp_ontap.models.performance_metric_io_type.PerformanceMetricIoTypeSchema", unknown=EXCLUDE, data_key="latency")
    r""" The latency field of the nvme_service_metric. """

    status = fields.Str(data_key="status")
    r""" Any errors associated with the sample. For example, if the aggregation of data over multiple nodes fails then any of the partial errors might be returned, "ok" on success, or "error" on any internal uncategorized failure. Whenever a sample collection is missed but done at a later time, it is back filled to the previous 15 second timestamp and tagged with "backfilled_data". "Inconsistent_ delta_time" is encountered when the time between two collections is not the same for all nodes. Therefore, the aggregated value might be over or under inflated. "Negative_delta" is returned when an expected monotonically increasing value has decreased in value. "Inconsistent_old_data" is returned when one or more nodes do not have the latest data.

Valid choices:

* ok
* error
* partial_no_data
* partial_no_response
* partial_other_error
* negative_delta
* not_found
* backfilled_data
* inconsistent_delta_time
* inconsistent_old_data
* partial_no_uuid """

    tcp = fields.Nested("netapp_ontap.models.performance_metric_svm.PerformanceMetricSvmSchema", unknown=EXCLUDE, data_key="tcp")
    r""" The tcp field of the nvme_service_metric. """

    throughput = fields.Nested("netapp_ontap.models.performance_metric_io_type_rwt.PerformanceMetricIoTypeRwtSchema", unknown=EXCLUDE, data_key="throughput")
    r""" The throughput field of the nvme_service_metric. """

    timestamp = ImpreciseDateTime(data_key="timestamp")
    r""" The timestamp of the performance data.

Example: 2017-01-25T11:20:13.000+0000 """

    @property
    def resource(self):
        return NvmeServiceMetric

    gettable_fields = [
        "links",
        "duration",
        "fc.links",
        "fc.duration",
        "fc.iops",
        "fc.latency",
        "fc.status",
        "fc.throughput",
        "fc.timestamp",
        "iops.other",
        "iops.read",
        "iops.total",
        "iops.write",
        "latency.other",
        "latency.read",
        "latency.total",
        "latency.write",
        "status",
        "tcp.links",
        "tcp.duration",
        "tcp.iops",
        "tcp.latency",
        "tcp.status",
        "tcp.throughput",
        "tcp.timestamp",
        "throughput.read",
        "throughput.total",
        "throughput.write",
        "timestamp",
    ]
    """links,duration,fc.links,fc.duration,fc.iops,fc.latency,fc.status,fc.throughput,fc.timestamp,iops.other,iops.read,iops.total,iops.write,latency.other,latency.read,latency.total,latency.write,status,tcp.links,tcp.duration,tcp.iops,tcp.latency,tcp.status,tcp.throughput,tcp.timestamp,throughput.read,throughput.total,throughput.write,timestamp,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NvmeServiceMetric(Resource):

    _schema = NvmeServiceMetricSchema
