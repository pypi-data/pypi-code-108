r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeEfficiencyPolicySchedule", "VolumeEfficiencyPolicyScheduleSchema"]
__pdoc__ = {
    "VolumeEfficiencyPolicyScheduleSchema.resource": False,
    "VolumeEfficiencyPolicySchedule": False,
}


class VolumeEfficiencyPolicyScheduleSchema(ResourceSchema):
    """The fields of the VolumeEfficiencyPolicySchedule object"""

    name = fields.Str(data_key="name")
    r""" Schedule at which volume efficiency policies are captured on the SVM. Some common schedules already defined in the system are hourly, daily, weekly, at 5 minute intervals, and at 8 hour intervals. Volume efficiency policies with custom schedules can be referenced.

Example: daily """

    @property
    def resource(self):
        return VolumeEfficiencyPolicySchedule

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class VolumeEfficiencyPolicySchedule(Resource):

    _schema = VolumeEfficiencyPolicyScheduleSchema
