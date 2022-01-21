r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AnalyticsInfoByModifiedTime", "AnalyticsInfoByModifiedTimeSchema"]
__pdoc__ = {
    "AnalyticsInfoByModifiedTimeSchema.resource": False,
    "AnalyticsInfoByModifiedTime": False,
}


class AnalyticsInfoByModifiedTimeSchema(ResourceSchema):
    """The fields of the AnalyticsInfoByModifiedTime object"""

    bytes_used = fields.Nested("netapp_ontap.models.analytics_histogram_by_time.AnalyticsHistogramByTimeSchema", unknown=EXCLUDE, data_key="bytes_used")
    r""" The bytes_used field of the analytics_info_by_modified_time. """

    @property
    def resource(self):
        return AnalyticsInfoByModifiedTime

    gettable_fields = [
        "bytes_used",
    ]
    """bytes_used,"""

    patchable_fields = [
        "bytes_used",
    ]
    """bytes_used,"""

    postable_fields = [
        "bytes_used",
    ]
    """bytes_used,"""


class AnalyticsInfoByModifiedTime(Resource):

    _schema = AnalyticsInfoByModifiedTimeSchema
