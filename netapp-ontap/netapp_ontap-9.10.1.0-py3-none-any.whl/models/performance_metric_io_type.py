r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["PerformanceMetricIoType", "PerformanceMetricIoTypeSchema"]
__pdoc__ = {
    "PerformanceMetricIoTypeSchema.resource": False,
    "PerformanceMetricIoType": False,
}


class PerformanceMetricIoTypeSchema(ResourceSchema):
    """The fields of the PerformanceMetricIoType object"""

    other = Size(data_key="other")
    r""" Performance metric for other I/O operations. Other I/O operations can be metadata operations, such as directory lookups and so on. """

    read = Size(data_key="read")
    r""" Performance metric for read I/O operations.

Example: 200 """

    total = Size(data_key="total")
    r""" Performance metric aggregated over all types of I/O operations.

Example: 1000 """

    write = Size(data_key="write")
    r""" Peformance metric for write I/O operations.

Example: 100 """

    @property
    def resource(self):
        return PerformanceMetricIoType

    gettable_fields = [
        "other",
        "read",
        "total",
        "write",
    ]
    """other,read,total,write,"""

    patchable_fields = [
        "other",
        "read",
        "total",
        "write",
    ]
    """other,read,total,write,"""

    postable_fields = [
        "other",
        "read",
        "total",
        "write",
    ]
    """other,read,total,write,"""


class PerformanceMetricIoType(Resource):

    _schema = PerformanceMetricIoTypeSchema
