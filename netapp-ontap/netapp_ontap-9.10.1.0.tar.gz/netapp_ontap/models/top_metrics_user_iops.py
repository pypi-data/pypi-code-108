r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["TopMetricsUserIops", "TopMetricsUserIopsSchema"]
__pdoc__ = {
    "TopMetricsUserIopsSchema.resource": False,
    "TopMetricsUserIops": False,
}


class TopMetricsUserIopsSchema(ResourceSchema):
    """The fields of the TopMetricsUserIops object"""

    error = fields.Nested("netapp_ontap.models.top_metric_value_error_bounds.TopMetricValueErrorBoundsSchema", unknown=EXCLUDE, data_key="error")
    r""" The error field of the top_metrics_user_iops. """

    read = Size(data_key="read")
    r""" Average number of read operations per second.

Example: 4 """

    write = Size(data_key="write")
    r""" Average number of write operations per second.

Example: 8 """

    @property
    def resource(self):
        return TopMetricsUserIops

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


class TopMetricsUserIops(Resource):

    _schema = TopMetricsUserIopsSchema
