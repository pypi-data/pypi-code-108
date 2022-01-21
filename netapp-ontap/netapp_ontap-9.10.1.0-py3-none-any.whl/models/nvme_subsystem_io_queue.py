r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NvmeSubsystemIoQueue", "NvmeSubsystemIoQueueSchema"]
__pdoc__ = {
    "NvmeSubsystemIoQueueSchema.resource": False,
    "NvmeSubsystemIoQueue": False,
}


class NvmeSubsystemIoQueueSchema(ResourceSchema):
    """The fields of the NvmeSubsystemIoQueue object"""

    default = fields.Nested("netapp_ontap.models.nvme_subsystem_io_queue_default.NvmeSubsystemIoQueueDefaultSchema", unknown=EXCLUDE, data_key="default")
    r""" The default field of the nvme_subsystem_io_queue. """

    @property
    def resource(self):
        return NvmeSubsystemIoQueue

    gettable_fields = [
        "default",
    ]
    """default,"""

    patchable_fields = [
        "default",
    ]
    """default,"""

    postable_fields = [
        "default",
    ]
    """default,"""


class NvmeSubsystemIoQueue(Resource):

    _schema = NvmeSubsystemIoQueueSchema
