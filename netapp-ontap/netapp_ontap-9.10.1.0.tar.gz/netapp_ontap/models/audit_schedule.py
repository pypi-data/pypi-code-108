r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AuditSchedule", "AuditScheduleSchema"]
__pdoc__ = {
    "AuditScheduleSchema.resource": False,
    "AuditSchedule": False,
}


class AuditScheduleSchema(ResourceSchema):
    """The fields of the AuditSchedule object"""

    days = fields.List(Size, data_key="days")
    r""" Specifies the day of the month schedule to rotate audit log. Leave empty for all. """

    hours = fields.List(Size, data_key="hours")
    r""" Specifies the hourly schedule to rotate audit log. Leave empty for all. """

    minutes = fields.List(Size, data_key="minutes")
    r""" Specifies the minutes schedule to rotate the audit log. """

    months = fields.List(Size, data_key="months")
    r""" Specifies the months schedule to rotate audit log. Leave empty for all. """

    weekdays = fields.List(Size, data_key="weekdays")
    r""" Specifies the weekdays schedule to rotate audit log. Leave empty for all. """

    @property
    def resource(self):
        return AuditSchedule

    gettable_fields = [
        "days",
        "hours",
        "minutes",
        "months",
        "weekdays",
    ]
    """days,hours,minutes,months,weekdays,"""

    patchable_fields = [
        "days",
        "hours",
        "minutes",
        "months",
        "weekdays",
    ]
    """days,hours,minutes,months,weekdays,"""

    postable_fields = [
        "days",
        "hours",
        "minutes",
        "months",
        "weekdays",
    ]
    """days,hours,minutes,months,weekdays,"""


class AuditSchedule(Resource):

    _schema = AuditScheduleSchema
