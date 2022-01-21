r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AnalyticsCollectionInfoByAccessedTimeBytesUsed", "AnalyticsCollectionInfoByAccessedTimeBytesUsedSchema"]
__pdoc__ = {
    "AnalyticsCollectionInfoByAccessedTimeBytesUsedSchema.resource": False,
    "AnalyticsCollectionInfoByAccessedTimeBytesUsed": False,
}


class AnalyticsCollectionInfoByAccessedTimeBytesUsedSchema(ResourceSchema):
    """The fields of the AnalyticsCollectionInfoByAccessedTimeBytesUsed object"""

    labels = fields.List(fields.Str, data_key="labels")
    r""" The labels field of the analytics_collection_info_by_accessed_time_bytes_used. """

    @property
    def resource(self):
        return AnalyticsCollectionInfoByAccessedTimeBytesUsed

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


class AnalyticsCollectionInfoByAccessedTimeBytesUsed(Resource):

    _schema = AnalyticsCollectionInfoByAccessedTimeBytesUsedSchema
