r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupRestoreToSnapshot", "ConsistencyGroupRestoreToSnapshotSchema"]
__pdoc__ = {
    "ConsistencyGroupRestoreToSnapshotSchema.resource": False,
    "ConsistencyGroupRestoreToSnapshot": False,
}


class ConsistencyGroupRestoreToSnapshotSchema(ResourceSchema):
    """The fields of the ConsistencyGroupRestoreToSnapshot object"""

    name = fields.Str(data_key="name")
    r""" The name of the consistency group's Snapshot copy to restore to. """

    uuid = fields.Str(data_key="uuid")
    r""" The UUID of the consistency group's Snapshot copy to restore to. """

    @property
    def resource(self):
        return ConsistencyGroupRestoreToSnapshot

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


class ConsistencyGroupRestoreToSnapshot(Resource):

    _schema = ConsistencyGroupRestoreToSnapshotSchema
