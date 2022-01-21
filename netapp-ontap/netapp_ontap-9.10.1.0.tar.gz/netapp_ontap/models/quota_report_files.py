r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["QuotaReportFiles", "QuotaReportFilesSchema"]
__pdoc__ = {
    "QuotaReportFilesSchema.resource": False,
    "QuotaReportFiles": False,
}


class QuotaReportFilesSchema(ResourceSchema):
    """The fields of the QuotaReportFiles object"""

    hard_limit = Size(data_key="hard_limit")
    r""" File hard limit """

    soft_limit = Size(data_key="soft_limit")
    r""" File soft limit """

    used = fields.Nested("netapp_ontap.models.quota_report_files_used.QuotaReportFilesUsedSchema", unknown=EXCLUDE, data_key="used")
    r""" The used field of the quota_report_files. """

    @property
    def resource(self):
        return QuotaReportFiles

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


class QuotaReportFiles(Resource):

    _schema = QuotaReportFilesSchema
