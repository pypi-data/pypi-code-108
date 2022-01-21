r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["QuotaReportUsers", "QuotaReportUsersSchema"]
__pdoc__ = {
    "QuotaReportUsersSchema.resource": False,
    "QuotaReportUsers": False,
}


class QuotaReportUsersSchema(ResourceSchema):
    """The fields of the QuotaReportUsers object"""

    id = fields.Str(data_key="id")
    r""" Quota target user ID """

    name = fields.Str(data_key="name")
    r""" Quota target user name """

    @property
    def resource(self):
        return QuotaReportUsers

    gettable_fields = [
        "id",
        "name",
    ]
    """id,name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class QuotaReportUsers(Resource):

    _schema = QuotaReportUsersSchema
