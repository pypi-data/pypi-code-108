r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AnalyticsHistogramByTime", "AnalyticsHistogramByTimeSchema"]
__pdoc__ = {
    "AnalyticsHistogramByTimeSchema.resource": False,
    "AnalyticsHistogramByTime": False,
}


class AnalyticsHistogramByTimeSchema(ResourceSchema):
    """The fields of the AnalyticsHistogramByTime object"""

    labels = fields.List(fields.Str, data_key="labels")
    r""" The labels field of the analytics_histogram_by_time. """

    newest_label = fields.Str(data_key="newest_label")
    r""" The newest time label with a non-zero histogram value. """

    oldest_label = fields.Str(data_key="oldest_label")
    r""" The oldest time label with a non-zero histogram value. """

    percentages = fields.List(fields.Number, data_key="percentages")
    r""" Percentages for this histogram

Example: [0.1,11.24,0.18,15.75,0.75,83.5,0] """

    values = fields.List(Size, data_key="values")
    r""" Values for this histogram

Example: [15925248,1735569408,27672576,2430595072,116105216,12889948160,0] """

    @property
    def resource(self):
        return AnalyticsHistogramByTime

    gettable_fields = [
        "labels",
        "newest_label",
        "oldest_label",
        "percentages",
        "values",
    ]
    """labels,newest_label,oldest_label,percentages,values,"""

    patchable_fields = [
        "labels",
        "newest_label",
        "oldest_label",
        "percentages",
        "values",
    ]
    """labels,newest_label,oldest_label,percentages,values,"""

    postable_fields = [
        "labels",
        "newest_label",
        "oldest_label",
        "percentages",
        "values",
    ]
    """labels,newest_label,oldest_label,percentages,values,"""


class AnalyticsHistogramByTime(Resource):

    _schema = AnalyticsHistogramByTimeSchema
