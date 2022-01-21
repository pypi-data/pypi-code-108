r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunMovement", "LunMovementSchema"]
__pdoc__ = {
    "LunMovementSchema.resource": False,
    "LunMovement": False,
}


class LunMovementSchema(ResourceSchema):
    """The fields of the LunMovement object"""

    max_throughput = Size(data_key="max_throughput")
    r""" The maximum data throughput, in bytes per second, that should be utilized in support of the LUN movement. This property can be used to throttle a transfer and limit its impact on the performance of the source and destination nodes. The specified value will be rounded up to the nearest megabyte.<br/>
If this property is not specified in a POST that begins a LUN movement, throttling is not applied to the data transfer.<br/>
For more information, see _Size properties_ in the _docs_ section of the ONTAP REST API documentation.<br/>
This property is valid only in a POST that begins a LUN movement or a PATCH when a LUN movement is already in process. """

    paths = fields.Nested("netapp_ontap.models.lun_movement_paths.LunMovementPathsSchema", unknown=EXCLUDE, data_key="paths")
    r""" The paths field of the lun_movement. """

    progress = fields.Nested("netapp_ontap.models.lun_movement_progress.LunMovementProgressSchema", unknown=EXCLUDE, data_key="progress")
    r""" The progress field of the lun_movement. """

    @property
    def resource(self):
        return LunMovement

    gettable_fields = [
        "max_throughput",
        "paths",
        "progress",
    ]
    """max_throughput,paths,progress,"""

    patchable_fields = [
        "max_throughput",
        "paths",
        "progress",
    ]
    """max_throughput,paths,progress,"""

    postable_fields = [
        "max_throughput",
        "paths",
    ]
    """max_throughput,paths,"""


class LunMovement(Resource):

    _schema = LunMovementSchema
