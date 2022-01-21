r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["QuotaRuleGroup", "QuotaRuleGroupSchema"]
__pdoc__ = {
    "QuotaRuleGroupSchema.resource": False,
    "QuotaRuleGroup": False,
}


class QuotaRuleGroupSchema(ResourceSchema):
    """The fields of the QuotaRuleGroup object"""

    id = fields.Str(data_key="id")
    r""" Quota target group ID """

    name = fields.Str(data_key="name")
    r""" Quota target group name """

    @property
    def resource(self):
        return QuotaRuleGroup

    gettable_fields = [
        "id",
        "name",
    ]
    """id,name,"""

    patchable_fields = [
        "id",
        "name",
    ]
    """id,name,"""

    postable_fields = [
        "id",
        "name",
    ]
    """id,name,"""


class QuotaRuleGroup(Resource):

    _schema = QuotaRuleGroupSchema
