r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["S3LogRetention", "S3LogRetentionSchema"]
__pdoc__ = {
    "S3LogRetentionSchema.resource": False,
    "S3LogRetention": False,
}


class S3LogRetentionSchema(ResourceSchema):
    """The fields of the S3LogRetention object"""

    count = Size(data_key="count")
    r""" Determines how many audit log files to retain before rotating the
oldest log file out. This is mutually exclusive with "duration". """

    duration = fields.Str(data_key="duration")
    r""" Specifies an ISO-8601 format date and time to retain the audit log file. The audit log files are
deleted once they reach the specified date/time. This is mutually exclusive with "count".


Example: P4DT12H30M5S """

    @property
    def resource(self):
        return S3LogRetention

    gettable_fields = [
        "count",
        "duration",
    ]
    """count,duration,"""

    patchable_fields = [
        "count",
        "duration",
    ]
    """count,duration,"""

    postable_fields = [
        "count",
        "duration",
    ]
    """count,duration,"""


class S3LogRetention(Resource):

    _schema = S3LogRetentionSchema
