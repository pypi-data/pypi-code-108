r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["TopMetricsFileThroughput", "TopMetricsFileThroughputSchema"]
__pdoc__ = {
    "TopMetricsFileThroughputSchema.resource": False,
    "TopMetricsFileThroughput": False,
}


class TopMetricsFileThroughputSchema(ResourceSchema):
    """The fields of the TopMetricsFileThroughput object"""

    error = fields.Nested("netapp_ontap.models.top_metric_value_error_bounds.TopMetricValueErrorBoundsSchema", unknown=EXCLUDE, data_key="error")
    r""" The error field of the top_metrics_file_throughput. """

    read = Size(data_key="read")
    r""" Average number of read bytes received per second.

Example: 2 """

    write = Size(data_key="write")
    r""" Average number of write bytes received per second.

Example: 20 """

    @property
    def resource(self):
        return TopMetricsFileThroughput

    gettable_fields = [
        "error",
        "read",
        "write",
    ]
    """error,read,write,"""

    patchable_fields = [
        "error",
    ]
    """error,"""

    postable_fields = [
        "error",
    ]
    """error,"""


class TopMetricsFileThroughput(Resource):

    _schema = TopMetricsFileThroughputSchema
