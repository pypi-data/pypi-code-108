r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["CifsDomainPasswordSchedule", "CifsDomainPasswordScheduleSchema"]
__pdoc__ = {
    "CifsDomainPasswordScheduleSchema.resource": False,
    "CifsDomainPasswordSchedule": False,
}


class CifsDomainPasswordScheduleSchema(ResourceSchema):
    """The fields of the CifsDomainPasswordSchedule object"""

    schedule_description = fields.Str(data_key="schedule_description")
    r""" Schedule description. """

    schedule_enabled = fields.Boolean(data_key="schedule_enabled")
    r""" Is password schedule enabled. """

    schedule_last_changed_time = ImpreciseDateTime(data_key="schedule_last_changed_time")
    r""" Last successful password change time. """

    schedule_randomized_minute = Size(data_key="schedule_randomized_minute")
    r""" Minutes within which schedule start can be randomized. """

    schedule_warn_message = fields.Str(data_key="schedule_warn_message")
    r""" Warning message in case job is deleted. """

    schedule_weekly_interval = Size(data_key="schedule_weekly_interval")
    r""" Interval in weeks for password change schedule. """

    @property
    def resource(self):
        return CifsDomainPasswordSchedule

    gettable_fields = [
        "schedule_description",
        "schedule_enabled",
        "schedule_last_changed_time",
        "schedule_randomized_minute",
        "schedule_warn_message",
        "schedule_weekly_interval",
    ]
    """schedule_description,schedule_enabled,schedule_last_changed_time,schedule_randomized_minute,schedule_warn_message,schedule_weekly_interval,"""

    patchable_fields = [
        "schedule_description",
        "schedule_enabled",
        "schedule_last_changed_time",
        "schedule_randomized_minute",
        "schedule_warn_message",
        "schedule_weekly_interval",
    ]
    """schedule_description,schedule_enabled,schedule_last_changed_time,schedule_randomized_minute,schedule_warn_message,schedule_weekly_interval,"""

    postable_fields = [
        "schedule_description",
        "schedule_enabled",
        "schedule_last_changed_time",
        "schedule_randomized_minute",
        "schedule_warn_message",
        "schedule_weekly_interval",
    ]
    """schedule_description,schedule_enabled,schedule_last_changed_time,schedule_randomized_minute,schedule_warn_message,schedule_weekly_interval,"""


class CifsDomainPasswordSchedule(Resource):

    _schema = CifsDomainPasswordScheduleSchema
