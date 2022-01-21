r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AnalyticsCollectionInfoByModifiedTimeBytesUsed", "AnalyticsCollectionInfoByModifiedTimeBytesUsedSchema"]
__pdoc__ = {
    "AnalyticsCollectionInfoByModifiedTimeBytesUsedSchema.resource": False,
    "AnalyticsCollectionInfoByModifiedTimeBytesUsed": False,
}


class AnalyticsCollectionInfoByModifiedTimeBytesUsedSchema(ResourceSchema):
    """The fields of the AnalyticsCollectionInfoByModifiedTimeBytesUsed object"""

    labels = fields.List(fields.Str, data_key="labels")
    r""" The labels field of the analytics_collection_info_by_modified_time_bytes_used. """

    @property
    def resource(self):
        return AnalyticsCollectionInfoByModifiedTimeBytesUsed

    gettable_fields = [
        "labels",
    ]
    """labels,"""

    patchable_fields = [
        "labels",
    ]
    """labels,"""

    postable_fields = [
        "labels",
    ]
    """labels,"""


class AnalyticsCollectionInfoByModifiedTimeBytesUsed(Resource):

    _schema = AnalyticsCollectionInfoByModifiedTimeBytesUsedSchema
