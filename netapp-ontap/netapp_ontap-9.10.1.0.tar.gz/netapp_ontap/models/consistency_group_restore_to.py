r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupRestoreTo", "ConsistencyGroupRestoreToSchema"]
__pdoc__ = {
    "ConsistencyGroupRestoreToSchema.resource": False,
    "ConsistencyGroupRestoreTo": False,
}


class ConsistencyGroupRestoreToSchema(ResourceSchema):
    """The fields of the ConsistencyGroupRestoreTo object"""

    snapshot = fields.Nested("netapp_ontap.models.consistency_group_restore_to_snapshot.ConsistencyGroupRestoreToSnapshotSchema", unknown=EXCLUDE, data_key="snapshot")
    r""" The snapshot field of the consistency_group_restore_to. """

    @property
    def resource(self):
        return ConsistencyGroupRestoreTo

    gettable_fields = [
        "snapshot",
    ]
    """snapshot,"""

    patchable_fields = [
        "snapshot",
    ]
    """snapshot,"""

    postable_fields = [
        "snapshot",
    ]
    """snapshot,"""


class ConsistencyGroupRestoreTo(Resource):

    _schema = ConsistencyGroupRestoreToSchema
