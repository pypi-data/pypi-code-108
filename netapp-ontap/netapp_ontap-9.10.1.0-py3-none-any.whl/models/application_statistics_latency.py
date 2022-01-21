r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationStatisticsLatency", "ApplicationStatisticsLatencySchema"]
__pdoc__ = {
    "ApplicationStatisticsLatencySchema.resource": False,
    "ApplicationStatisticsLatency": False,
}


class ApplicationStatisticsLatencySchema(ResourceSchema):
    """The fields of the ApplicationStatisticsLatency object"""

    average = Size(data_key="average")
    r""" The cumulative average response time in microseconds for this component. """

    raw = Size(data_key="raw")
    r""" The cumulative response time in microseconds for this component. """

    @property
    def resource(self):
        return ApplicationStatisticsLatency

    gettable_fields = [
        "average",
        "raw",
    ]
    """average,raw,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationStatisticsLatency(Resource):

    _schema = ApplicationStatisticsLatencySchema
