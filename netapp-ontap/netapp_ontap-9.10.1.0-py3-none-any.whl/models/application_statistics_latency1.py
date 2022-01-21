r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationStatisticsLatency1", "ApplicationStatisticsLatency1Schema"]
__pdoc__ = {
    "ApplicationStatisticsLatency1Schema.resource": False,
    "ApplicationStatisticsLatency1": False,
}


class ApplicationStatisticsLatency1Schema(ResourceSchema):
    """The fields of the ApplicationStatisticsLatency1 object"""

    average = Size(data_key="average")
    r""" The cumulative average response time in microseconds for this application. """

    raw = Size(data_key="raw")
    r""" The cumulative response time in microseconds for this application. """

    @property
    def resource(self):
        return ApplicationStatisticsLatency1

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


class ApplicationStatisticsLatency1(Resource):

    _schema = ApplicationStatisticsLatency1Schema
