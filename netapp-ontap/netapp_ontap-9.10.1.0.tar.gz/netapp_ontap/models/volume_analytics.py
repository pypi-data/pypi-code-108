r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeAnalytics", "VolumeAnalyticsSchema"]
__pdoc__ = {
    "VolumeAnalyticsSchema.resource": False,
    "VolumeAnalytics": False,
}


class VolumeAnalyticsSchema(ResourceSchema):
    """The fields of the VolumeAnalytics object"""

    scan_progress = Size(data_key="scan_progress")
    r""" Percentage of files in the volume that the file system analytics initialization scan has processed. Only returned when the state is `initializing`.

Example: 17 """

    state = fields.Str(data_key="state")
    r""" File system analytics state of the volume. If this value is "on", ONTAP collects extra file system analytics information for all directories on the volume.  There will be a slight impact to I/O performance to collect this information. If this value is "off", file system analytics information is not collected and not available to be viewed. If this value is "initializing", that means file system analytics was recently turned on, and the initialization scan to gather information all all existing files and directories is currently running. If this value is 'unknown' that means there was an internal error when determining the file system analytics state for the volume.

Valid choices:

* unknown
* initializing
* off
* on """

    supported = fields.Boolean(data_key="supported")
    r""" This field indicates whether or not file system analytics is supported on the volume. If file system analytics is not supported, the reason will be specified in the "analytics.unsupported_reason" field. """

    unsupported_reason = fields.Nested("netapp_ontap.models.volume_analytics_unsupported_reason.VolumeAnalyticsUnsupportedReasonSchema", unknown=EXCLUDE, data_key="unsupported_reason")
    r""" The unsupported_reason field of the volume_analytics. """

    @property
    def resource(self):
        return VolumeAnalytics

    gettable_fields = [
        "scan_progress",
        "state",
        "supported",
        "unsupported_reason",
    ]
    """scan_progress,state,supported,unsupported_reason,"""

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


class VolumeAnalytics(Resource):

    _schema = VolumeAnalyticsSchema
