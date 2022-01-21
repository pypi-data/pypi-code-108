r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SnapmirrorPolicyRule", "SnapmirrorPolicyRuleSchema"]
__pdoc__ = {
    "SnapmirrorPolicyRuleSchema.resource": False,
    "SnapmirrorPolicyRule": False,
}


class SnapmirrorPolicyRuleSchema(ResourceSchema):
    """The fields of the SnapmirrorPolicyRule object"""

    count = Size(data_key="count")
    r""" Number of Snapshot copies to be kept for retention.

Example: 7 """

    creation_schedule = fields.Nested("netapp_ontap.resources.schedule.ScheduleSchema", unknown=EXCLUDE, data_key="creation_schedule")
    r""" The creation_schedule field of the snapmirror_policy_rule. """

    label = fields.Str(data_key="label")
    r""" Snapshot copy label

Example: hourly """

    prefix = fields.Str(data_key="prefix")
    r""" Specifies the prefix for the Snapshot copy name to be created as per the schedule. If no value is specified, then the label is used as the prefix. """

    @property
    def resource(self):
        return SnapmirrorPolicyRule

    gettable_fields = [
        "count",
        "creation_schedule.links",
        "creation_schedule.name",
        "creation_schedule.uuid",
        "label",
        "prefix",
    ]
    """count,creation_schedule.links,creation_schedule.name,creation_schedule.uuid,label,prefix,"""

    patchable_fields = [
        "count",
        "creation_schedule.name",
        "creation_schedule.uuid",
        "label",
        "prefix",
    ]
    """count,creation_schedule.name,creation_schedule.uuid,label,prefix,"""

    postable_fields = [
        "count",
        "creation_schedule.name",
        "creation_schedule.uuid",
        "label",
        "prefix",
    ]
    """count,creation_schedule.name,creation_schedule.uuid,label,prefix,"""


class SnapmirrorPolicyRule(Resource):

    _schema = SnapmirrorPolicyRuleSchema
