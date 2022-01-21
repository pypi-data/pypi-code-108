r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NvmeSubsystemControllerIoQueue", "NvmeSubsystemControllerIoQueueSchema"]
__pdoc__ = {
    "NvmeSubsystemControllerIoQueueSchema.resource": False,
    "NvmeSubsystemControllerIoQueue": False,
}


class NvmeSubsystemControllerIoQueueSchema(ResourceSchema):
    """The fields of the NvmeSubsystemControllerIoQueue object"""

    count = Size(data_key="count")
    r""" The number of I/O queues available to the controller. """

    depth = fields.List(Size, data_key="depth")
    r""" The depths of the I/O queues. """

    @property
    def resource(self):
        return NvmeSubsystemControllerIoQueue

    gettable_fields = [
        "count",
        "depth",
    ]
    """count,depth,"""

    patchable_fields = [
        "depth",
    ]
    """depth,"""

    postable_fields = [
        "depth",
    ]
    """depth,"""


class NvmeSubsystemControllerIoQueue(Resource):

    _schema = NvmeSubsystemControllerIoQueueSchema
