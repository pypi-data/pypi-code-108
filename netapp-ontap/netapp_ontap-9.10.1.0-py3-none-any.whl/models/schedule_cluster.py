r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ScheduleCluster", "ScheduleClusterSchema"]
__pdoc__ = {
    "ScheduleClusterSchema.resource": False,
    "ScheduleCluster": False,
}


class ScheduleClusterSchema(ResourceSchema):
    """The fields of the ScheduleCluster object"""

    name = fields.Str(data_key="name")
    r""" Cluster name

Example: cluster1 """

    uuid = fields.Str(data_key="uuid")
    r""" Cluster UUID

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return ScheduleCluster

    gettable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    patchable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    postable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""


class ScheduleCluster(Resource):

    _schema = ScheduleClusterSchema
