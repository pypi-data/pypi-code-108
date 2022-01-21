r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AggregateBlockStorageMirror", "AggregateBlockStorageMirrorSchema"]
__pdoc__ = {
    "AggregateBlockStorageMirrorSchema.resource": False,
    "AggregateBlockStorageMirror": False,
}


class AggregateBlockStorageMirrorSchema(ResourceSchema):
    """The fields of the AggregateBlockStorageMirror object"""

    enabled = fields.Boolean(data_key="enabled")
    r""" Aggregate is SyncMirror protected

Example: false """

    state = fields.Str(data_key="state")
    r""" The state field of the aggregate_block_storage_mirror.

Valid choices:

* unmirrored
* normal
* degraded
* resynchronizing
* failed """

    @property
    def resource(self):
        return AggregateBlockStorageMirror

    gettable_fields = [
        "enabled",
        "state",
    ]
    """enabled,state,"""

    patchable_fields = [
        "enabled",
    ]
    """enabled,"""

    postable_fields = [
        "enabled",
    ]
    """enabled,"""


class AggregateBlockStorageMirror(Resource):

    _schema = AggregateBlockStorageMirrorSchema
