r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationStatisticsIops", "ApplicationStatisticsIopsSchema"]
__pdoc__ = {
    "ApplicationStatisticsIopsSchema.resource": False,
    "ApplicationStatisticsIops": False,
}


class ApplicationStatisticsIopsSchema(ResourceSchema):
    """The fields of the ApplicationStatisticsIops object"""

    per_tb = Size(data_key="per_tb")
    r""" The number of IOPS per terabyte of logical space currently being used by the application component. """

    total = Size(data_key="total")
    r""" The total number of IOPS being used by the application component. """

    @property
    def resource(self):
        return ApplicationStatisticsIops

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


class ApplicationStatisticsIops(Resource):

    _schema = ApplicationStatisticsIopsSchema
