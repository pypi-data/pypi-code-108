r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["TopMetricsClientIops", "TopMetricsClientIopsSchema"]
__pdoc__ = {
    "TopMetricsClientIopsSchema.resource": False,
    "TopMetricsClientIops": False,
}


class TopMetricsClientIopsSchema(ResourceSchema):
    """The fields of the TopMetricsClientIops object"""

    error = fields.Nested("netapp_ontap.models.top_metric_value_error_bounds.TopMetricValueErrorBoundsSchema", unknown=EXCLUDE, data_key="error")
    r""" The error field of the top_metrics_client_iops. """

    read = Size(data_key="read")
    r""" Average number of read operations per second.

Example: 5 """

    write = Size(data_key="write")
    r""" Average number of write operations per second.

Example: 10 """

    @property
    def resource(self):
        return TopMetricsClientIops

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


class TopMetricsClientIops(Resource):

    _schema = TopMetricsClientIopsSchema
