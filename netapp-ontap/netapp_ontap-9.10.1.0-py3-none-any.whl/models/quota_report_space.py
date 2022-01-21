r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["QuotaReportSpace", "QuotaReportSpaceSchema"]
__pdoc__ = {
    "QuotaReportSpaceSchema.resource": False,
    "QuotaReportSpace": False,
}


class QuotaReportSpaceSchema(ResourceSchema):
    """The fields of the QuotaReportSpace object"""

    hard_limit = Size(data_key="hard_limit")
    r""" Space hard limit in bytes """

    soft_limit = Size(data_key="soft_limit")
    r""" Space soft limit in bytes """

    used = fields.Nested("netapp_ontap.models.quota_report_space_used.QuotaReportSpaceUsedSchema", unknown=EXCLUDE, data_key="used")
    r""" The used field of the quota_report_space. """

    @property
    def resource(self):
        return QuotaReportSpace

    gettable_fields = [
        "hard_limit",
        "soft_limit",
        "used",
    ]
    """hard_limit,soft_limit,used,"""

    patchable_fields = [
        "used",
    ]
    """used,"""

    postable_fields = [
        "used",
    ]
    """used,"""


class QuotaReportSpace(Resource):

    _schema = QuotaReportSpaceSchema
