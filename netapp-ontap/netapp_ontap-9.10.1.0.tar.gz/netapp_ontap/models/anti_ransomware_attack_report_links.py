r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AntiRansomwareAttackReportLinks", "AntiRansomwareAttackReportLinksSchema"]
__pdoc__ = {
    "AntiRansomwareAttackReportLinksSchema.resource": False,
    "AntiRansomwareAttackReportLinks": False,
}


class AntiRansomwareAttackReportLinksSchema(ResourceSchema):
    """The fields of the AntiRansomwareAttackReportLinks object"""

    suspects = fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="suspects")
    r""" The suspects field of the anti_ransomware_attack_report_links. """

    @property
    def resource(self):
        return AntiRansomwareAttackReportLinks

    gettable_fields = [
        "suspects",
    ]
    """suspects,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AntiRansomwareAttackReportLinks(Resource):

    _schema = AntiRansomwareAttackReportLinksSchema
