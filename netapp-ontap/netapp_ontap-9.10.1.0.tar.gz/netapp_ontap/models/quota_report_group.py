r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["QuotaReportGroup", "QuotaReportGroupSchema"]
__pdoc__ = {
    "QuotaReportGroupSchema.resource": False,
    "QuotaReportGroup": False,
}


class QuotaReportGroupSchema(ResourceSchema):
    """The fields of the QuotaReportGroup object"""

    id = fields.Str(data_key="id")
    r""" Quota target group ID """

    name = fields.Str(data_key="name")
    r""" Quota target group name """

    @property
    def resource(self):
        return QuotaReportGroup

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


class QuotaReportGroup(Resource):

    _schema = QuotaReportGroupSchema
