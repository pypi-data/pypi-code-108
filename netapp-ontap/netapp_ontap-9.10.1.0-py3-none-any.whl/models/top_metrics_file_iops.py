r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["TopMetricsFileIops", "TopMetricsFileIopsSchema"]
__pdoc__ = {
    "TopMetricsFileIopsSchema.resource": False,
    "TopMetricsFileIops": False,
}


class TopMetricsFileIopsSchema(ResourceSchema):
    """The fields of the TopMetricsFileIops object"""

    error = fields.Nested("netapp_ontap.models.top_metric_value_error_bounds.TopMetricValueErrorBoundsSchema", unknown=EXCLUDE, data_key="error")
    r""" The error field of the top_metrics_file_iops. """

    read = Size(data_key="read")
    r""" Average number of read operations per second.

Example: 5 """

    write = Size(data_key="write")
    r""" Average number of write operations per second.

Example: 4 """

    @property
    def resource(self):
        return TopMetricsFileIops

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


class TopMetricsFileIops(Resource):

    _schema = TopMetricsFileIopsSchema
