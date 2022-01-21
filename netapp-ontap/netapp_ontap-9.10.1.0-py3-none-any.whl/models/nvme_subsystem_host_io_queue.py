r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NvmeSubsystemHostIoQueue", "NvmeSubsystemHostIoQueueSchema"]
__pdoc__ = {
    "NvmeSubsystemHostIoQueueSchema.resource": False,
    "NvmeSubsystemHostIoQueue": False,
}


class NvmeSubsystemHostIoQueueSchema(ResourceSchema):
    """The fields of the NvmeSubsystemHostIoQueue object"""

    count = Size(data_key="count")
    r""" The number of I/O queue pairs. The default value is inherited from the owning NVMe subsystem.


Example: 4 """

    depth = Size(data_key="depth")
    r""" The I/O queue depth. The default value is inherited from the owning NVMe subsystem.


Example: 32 """

    @property
    def resource(self):
        return NvmeSubsystemHostIoQueue

    gettable_fields = [
        "count",
        "depth",
    ]
    """count,depth,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NvmeSubsystemHostIoQueue(Resource):

    _schema = NvmeSubsystemHostIoQueueSchema
