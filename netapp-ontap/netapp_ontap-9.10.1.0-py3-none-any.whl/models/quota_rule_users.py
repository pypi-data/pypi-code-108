r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["QuotaRuleUsers", "QuotaRuleUsersSchema"]
__pdoc__ = {
    "QuotaRuleUsersSchema.resource": False,
    "QuotaRuleUsers": False,
}


class QuotaRuleUsersSchema(ResourceSchema):
    """The fields of the QuotaRuleUsers object"""

    id = fields.Str(data_key="id")
    r""" Quota target user ID """

    name = fields.Str(data_key="name")
    r""" Quota target user name """

    @property
    def resource(self):
        return QuotaRuleUsers

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


class QuotaRuleUsers(Resource):

    _schema = QuotaRuleUsersSchema
