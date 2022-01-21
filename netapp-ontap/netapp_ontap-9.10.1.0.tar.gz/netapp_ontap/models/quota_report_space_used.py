r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["QuotaReportSpaceUsed", "QuotaReportSpaceUsedSchema"]
__pdoc__ = {
    "QuotaReportSpaceUsedSchema.resource": False,
    "QuotaReportSpaceUsed": False,
}


class QuotaReportSpaceUsedSchema(ResourceSchema):
    """The fields of the QuotaReportSpaceUsed object"""

    hard_limit_percent = Size(data_key="hard_limit_percent")
    r""" Total space used as a percentage of space hard limit """

    soft_limit_percent = Size(data_key="soft_limit_percent")
    r""" Total space used as a percentage of space soft limit """

    total = Size(data_key="total")
    r""" Total space used """

    @property
    def resource(self):
        return QuotaReportSpaceUsed

    gettable_fields = [
        "hard_limit_percent",
        "soft_limit_percent",
        "total",
    ]
    """hard_limit_percent,soft_limit_percent,total,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class QuotaReportSpaceUsed(Resource):

    _schema = QuotaReportSpaceUsedSchema
