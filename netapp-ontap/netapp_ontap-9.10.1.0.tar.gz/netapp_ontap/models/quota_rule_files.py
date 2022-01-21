r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["QuotaRuleFiles", "QuotaRuleFilesSchema"]
__pdoc__ = {
    "QuotaRuleFilesSchema.resource": False,
    "QuotaRuleFiles": False,
}


class QuotaRuleFilesSchema(ResourceSchema):
    """The fields of the QuotaRuleFiles object"""

    hard_limit = Size(data_key="hard_limit")
    r""" This parameter specifies the hard limit for files. This is valid in POST or PATCH. """

    soft_limit = Size(data_key="soft_limit")
    r""" This parameter specifies the soft limit for files. This is valid in POST or PATCH. """

    @property
    def resource(self):
        return QuotaRuleFiles

    gettable_fields = [
        "hard_limit",
        "soft_limit",
    ]
    """hard_limit,soft_limit,"""

    patchable_fields = [
        "hard_limit",
        "soft_limit",
    ]
    """hard_limit,soft_limit,"""

    postable_fields = [
        "hard_limit",
        "soft_limit",
    ]
    """hard_limit,soft_limit,"""


class QuotaRuleFiles(Resource):

    _schema = QuotaRuleFilesSchema
