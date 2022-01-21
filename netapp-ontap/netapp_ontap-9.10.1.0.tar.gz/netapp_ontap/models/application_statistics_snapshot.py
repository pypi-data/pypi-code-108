r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationStatisticsSnapshot", "ApplicationStatisticsSnapshotSchema"]
__pdoc__ = {
    "ApplicationStatisticsSnapshotSchema.resource": False,
    "ApplicationStatisticsSnapshot": False,
}


class ApplicationStatisticsSnapshotSchema(ResourceSchema):
    """The fields of the ApplicationStatisticsSnapshot object"""

    reserve = Size(data_key="reserve")
    r""" The amount of space reserved by the system for Snapshot copies. """

    used = Size(data_key="used")
    r""" The amount of spacing currently in use by the system to store Snapshot copies. """

    @property
    def resource(self):
        return ApplicationStatisticsSnapshot

    gettable_fields = [
        "reserve",
        "used",
    ]
    """reserve,used,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationStatisticsSnapshot(Resource):

    _schema = ApplicationStatisticsSnapshotSchema
