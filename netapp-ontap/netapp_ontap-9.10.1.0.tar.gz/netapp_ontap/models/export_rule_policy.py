r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ExportRulePolicy", "ExportRulePolicySchema"]
__pdoc__ = {
    "ExportRulePolicySchema.resource": False,
    "ExportRulePolicy": False,
}


class ExportRulePolicySchema(ResourceSchema):
    """The fields of the ExportRulePolicy object"""

    id = Size(data_key="id")
    r""" Export policy ID """

    name = fields.Str(data_key="name")
    r""" Export policy name """

    @property
    def resource(self):
        return ExportRulePolicy

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


class ExportRulePolicy(Resource):

    _schema = ExportRulePolicySchema
