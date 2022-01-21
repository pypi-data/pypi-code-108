r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SnapshotPolicySchedule1", "SnapshotPolicySchedule1Schema"]
__pdoc__ = {
    "SnapshotPolicySchedule1Schema.resource": False,
    "SnapshotPolicySchedule1": False,
}


class SnapshotPolicySchedule1Schema(ResourceSchema):
    """The fields of the SnapshotPolicySchedule1 object"""

    name = fields.Str(data_key="name")
    r""" Schedule at which Snapshot copies are captured on the volume. Some common schedules already defined in the system are hourly, daily, weekly, at 15 minute intervals, and at 5 minute intervals. Snapshot copy policies with custom schedules can be referenced.

Example: hourly """

    @property
    def resource(self):
        return SnapshotPolicySchedule1

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


class SnapshotPolicySchedule1(Resource):

    _schema = SnapshotPolicySchedule1Schema
