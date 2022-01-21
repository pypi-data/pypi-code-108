r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationStatisticsIops1", "ApplicationStatisticsIops1Schema"]
__pdoc__ = {
    "ApplicationStatisticsIops1Schema.resource": False,
    "ApplicationStatisticsIops1": False,
}


class ApplicationStatisticsIops1Schema(ResourceSchema):
    """The fields of the ApplicationStatisticsIops1 object"""

    per_tb = Size(data_key="per_tb")
    r""" The number of IOPS per terabyte of logical space currently being used by the application. """

    total = Size(data_key="total")
    r""" The total number of IOPS being used by the application. """

    @property
    def resource(self):
        return ApplicationStatisticsIops1

    gettable_fields = [
        "per_tb",
        "total",
    ]
    """per_tb,total,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationStatisticsIops1(Resource):

    _schema = ApplicationStatisticsIops1Schema
