r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunMovementProgress", "LunMovementProgressSchema"]
__pdoc__ = {
    "LunMovementProgressSchema.resource": False,
    "LunMovementProgress": False,
}


class LunMovementProgressSchema(ResourceSchema):
    """The fields of the LunMovementProgress object"""

    elapsed = Size(data_key="elapsed")
    r""" The amount of time that has elapsed since the start of the LUN movement, in seconds. """

    failure = fields.Nested("netapp_ontap.models.error.ErrorSchema", unknown=EXCLUDE, data_key="failure")
    r""" Error information provided if the asynchronous LUN movement operation fails. """

    percent_complete = Size(data_key="percent_complete")
    r""" The percentage completed of the LUN movement. """

    state = fields.Str(data_key="state")
    r""" The state of the LUN movement.<br/>
Valid in PATCH when an LUN movement is active. Set to _paused_ to pause a LUN movement. Set to _replicating_ to resume a paused LUN movement.


Valid choices:

* preparing
* replicating
* paused
* paused_error
* complete
* reverting
* failed """

    volume_snapshot_blocked = fields.Boolean(data_key="volume_snapshot_blocked")
    r""" This property reports if volume Snapshot copies are blocked by the LUN movement. This property can be polled to identify when volume Snapshot copies can be resumed after beginning a LUN movement. """

    @property
    def resource(self):
        return LunMovementProgress

    gettable_fields = [
        "elapsed",
        "failure",
        "percent_complete",
        "state",
        "volume_snapshot_blocked",
    ]
    """elapsed,failure,percent_complete,state,volume_snapshot_blocked,"""

    patchable_fields = [
        "state",
    ]
    """state,"""

    postable_fields = [
    ]
    """"""


class LunMovementProgress(Resource):

    _schema = LunMovementProgressSchema
