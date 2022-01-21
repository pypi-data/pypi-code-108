r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AggregateSpaceSnapshot", "AggregateSpaceSnapshotSchema"]
__pdoc__ = {
    "AggregateSpaceSnapshotSchema.resource": False,
    "AggregateSpaceSnapshot": False,
}


class AggregateSpaceSnapshotSchema(ResourceSchema):
    """The fields of the AggregateSpaceSnapshot object"""

    available = Size(data_key="available")
    r""" Available space for Snapshot copies in bytes

Example: 2000 """

    reserve_percent = Size(data_key="reserve_percent")
    r""" Percentage of space reserved for Snapshot copies

Example: 20 """

    total = Size(data_key="total")
    r""" Total space for Snapshot copies in bytes

Example: 5000 """

    used = Size(data_key="used")
    r""" Space used by Snapshot copies in bytes

Example: 3000 """

    used_percent = Size(data_key="used_percent")
    r""" Percentage of disk space used by Snapshot copies

Example: 45 """

    @property
    def resource(self):
        return AggregateSpaceSnapshot

    gettable_fields = [
        "available",
        "reserve_percent",
        "total",
        "used",
        "used_percent",
    ]
    """available,reserve_percent,total,used,used_percent,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AggregateSpaceSnapshot(Resource):

    _schema = AggregateSpaceSnapshotSchema
