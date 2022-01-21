r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AnalyticsCollectionInfoByModifiedTime", "AnalyticsCollectionInfoByModifiedTimeSchema"]
__pdoc__ = {
    "AnalyticsCollectionInfoByModifiedTimeSchema.resource": False,
    "AnalyticsCollectionInfoByModifiedTime": False,
}


class AnalyticsCollectionInfoByModifiedTimeSchema(ResourceSchema):
    """The fields of the AnalyticsCollectionInfoByModifiedTime object"""

    bytes_used = fields.Nested("netapp_ontap.models.analytics_collection_info_by_modified_time_bytes_used.AnalyticsCollectionInfoByModifiedTimeBytesUsedSchema", unknown=EXCLUDE, data_key="bytes_used")
    r""" The bytes_used field of the analytics_collection_info_by_modified_time. """

    @property
    def resource(self):
        return AnalyticsCollectionInfoByModifiedTime

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


class AnalyticsCollectionInfoByModifiedTime(Resource):

    _schema = AnalyticsCollectionInfoByModifiedTimeSchema
