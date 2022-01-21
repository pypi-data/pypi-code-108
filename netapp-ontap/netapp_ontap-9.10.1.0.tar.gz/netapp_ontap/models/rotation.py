r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Rotation", "RotationSchema"]
__pdoc__ = {
    "RotationSchema.resource": False,
    "Rotation": False,
}


class RotationSchema(ResourceSchema):
    """The fields of the Rotation object"""

    now = fields.Boolean(data_key="now")
    r""" Manually rotates the audit logs. Optional in PATCH only. Not available in POST. """

    schedule = fields.Nested("netapp_ontap.models.audit_schedule.AuditScheduleSchema", unknown=EXCLUDE, data_key="schedule")
    r""" The schedule field of the rotation. """

    size = Size(data_key="size")
    r""" Rotates logs based on log size in bytes. """

    @property
    def resource(self):
        return Rotation

    gettable_fields = [
        "schedule",
        "size",
    ]
    """schedule,size,"""

    patchable_fields = [
        "now",
        "schedule",
        "size",
    ]
    """now,schedule,size,"""

    postable_fields = [
        "schedule",
        "size",
    ]
    """schedule,size,"""


class Rotation(Resource):

    _schema = RotationSchema
