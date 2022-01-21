r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeActivityTracking", "VolumeActivityTrackingSchema"]
__pdoc__ = {
    "VolumeActivityTrackingSchema.resource": False,
    "VolumeActivityTracking": False,
}


class VolumeActivityTrackingSchema(ResourceSchema):
    """The fields of the VolumeActivityTracking object"""

    state = fields.Str(data_key="state")
    r""" Activity tracking state of the volume. If this value is "on", ONTAP collects top metrics information for the volume in real time. There is a slight impact to I/O performance in order to collect this information. If this value is "off", no activity tracking information is collected or available to view.

Valid choices:

* off
* on """

    supported = fields.Boolean(data_key="supported")
    r""" This field indicates whether or not volume activity tracking is supported on the volume. If volume activity tracking is not supported, the reason why is provided in the "activity_tracking.unsupported_reason" field. """

    unsupported_reason = fields.Nested("netapp_ontap.models.volume_activity_tracking_unsupported_reason.VolumeActivityTrackingUnsupportedReasonSchema", unknown=EXCLUDE, data_key="unsupported_reason")
    r""" The unsupported_reason field of the volume_activity_tracking. """

    @property
    def resource(self):
        return VolumeActivityTracking

    gettable_fields = [
        "state",
        "supported",
        "unsupported_reason",
    ]
    """state,supported,unsupported_reason,"""

    patchable_fields = [
        "state",
        "unsupported_reason",
    ]
    """state,unsupported_reason,"""

    postable_fields = [
        "state",
        "unsupported_reason",
    ]
    """state,unsupported_reason,"""


class VolumeActivityTracking(Resource):

    _schema = VolumeActivityTrackingSchema
