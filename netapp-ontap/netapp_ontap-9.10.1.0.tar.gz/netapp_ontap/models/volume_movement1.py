r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeMovement1", "VolumeMovement1Schema"]
__pdoc__ = {
    "VolumeMovement1Schema.resource": False,
    "VolumeMovement1": False,
}


class VolumeMovement1Schema(ResourceSchema):
    """The fields of the VolumeMovement1 object"""

    cutover_window = Size(data_key="cutover_window")
    r""" Time window in seconds for cutover. The allowed range is between 30 to 300 seconds.

Example: 30 """

    destination_aggregate = fields.Nested("netapp_ontap.resources.aggregate.AggregateSchema", unknown=EXCLUDE, data_key="destination_aggregate")
    r""" The destination_aggregate field of the volume_movement1. """

    percent_complete = Size(data_key="percent_complete")
    r""" Completion percentage """

    start_time = ImpreciseDateTime(data_key="start_time")
    r""" Start time of volume move.

Example: 2020-12-07T08:45:12.000+0000 """

    state = fields.Str(data_key="state")
    r""" State of volume move operation. PATCH the state to "aborted" to abort the move operation. PATCH the state to "cutover" to trigger cutover. PATCH the state to "paused" to pause the volume move operation in progress. PATCH the state to "replicating" to resume the paused volume move operation. PATCH the state to "cutover_wait" to go into cutover manually. When volume move operation is waiting to go into "cutover" state, this is indicated by the "cutover_pending" state. A change of state is only supported if volume movement is in progress.

Valid choices:

* aborted
* cutover
* cutover_wait
* cutover_pending
* failed
* paused
* queued
* replicating
* success """

    tiering_policy = fields.Str(data_key="tiering_policy")
    r""" Tiering policy for FabricPool

Valid choices:

* all
* auto
* backup
* none
* snapshot_only """

    @property
    def resource(self):
        return VolumeMovement1

    gettable_fields = [
        "cutover_window",
        "destination_aggregate.links",
        "destination_aggregate.name",
        "destination_aggregate.uuid",
        "percent_complete",
        "start_time",
        "state",
    ]
    """cutover_window,destination_aggregate.links,destination_aggregate.name,destination_aggregate.uuid,percent_complete,start_time,state,"""

    patchable_fields = [
        "cutover_window",
        "destination_aggregate.name",
        "destination_aggregate.uuid",
        "state",
        "tiering_policy",
    ]
    """cutover_window,destination_aggregate.name,destination_aggregate.uuid,state,tiering_policy,"""

    postable_fields = [
        "cutover_window",
        "destination_aggregate.name",
        "destination_aggregate.uuid",
        "state",
    ]
    """cutover_window,destination_aggregate.name,destination_aggregate.uuid,state,"""


class VolumeMovement1(Resource):

    _schema = VolumeMovement1Schema
