r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AnalyticsInfo", "AnalyticsInfoSchema"]
__pdoc__ = {
    "AnalyticsInfoSchema.resource": False,
    "AnalyticsInfo": False,
}


class AnalyticsInfoSchema(ResourceSchema):
    """The fields of the AnalyticsInfo object"""

    by_accessed_time = fields.Nested("netapp_ontap.models.analytics_info_by_accessed_time.AnalyticsInfoByAccessedTimeSchema", unknown=EXCLUDE, data_key="by_accessed_time")
    r""" The by_accessed_time field of the analytics_info. """

    by_modified_time = fields.Nested("netapp_ontap.models.analytics_info_by_modified_time.AnalyticsInfoByModifiedTimeSchema", unknown=EXCLUDE, data_key="by_modified_time")
    r""" The by_modified_time field of the analytics_info. """

    bytes_used = Size(data_key="bytes_used")
    r""" Number of bytes used on-disk

Example: 15436648448 """

    file_count = Size(data_key="file_count")
    r""" Number of descendants

Example: 21134 """

    subdir_count = Size(data_key="subdir_count")
    r""" Number of sub directories

Example: 35 """

    @property
    def resource(self):
        return AnalyticsInfo

    gettable_fields = [
        "by_accessed_time",
        "by_modified_time",
        "bytes_used",
        "file_count",
        "subdir_count",
    ]
    """by_accessed_time,by_modified_time,bytes_used,file_count,subdir_count,"""

    patchable_fields = [
        "by_accessed_time",
        "by_modified_time",
        "bytes_used",
        "file_count",
        "subdir_count",
    ]
    """by_accessed_time,by_modified_time,bytes_used,file_count,subdir_count,"""

    postable_fields = [
        "by_accessed_time",
        "by_modified_time",
        "bytes_used",
        "file_count",
        "subdir_count",
    ]
    """by_accessed_time,by_modified_time,bytes_used,file_count,subdir_count,"""


class AnalyticsInfo(Resource):

    _schema = AnalyticsInfoSchema
