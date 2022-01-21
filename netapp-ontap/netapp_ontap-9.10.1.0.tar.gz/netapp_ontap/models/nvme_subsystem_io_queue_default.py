r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NvmeSubsystemIoQueueDefault", "NvmeSubsystemIoQueueDefaultSchema"]
__pdoc__ = {
    "NvmeSubsystemIoQueueDefaultSchema.resource": False,
    "NvmeSubsystemIoQueueDefault": False,
}


class NvmeSubsystemIoQueueDefaultSchema(ResourceSchema):
    """The fields of the NvmeSubsystemIoQueueDefault object"""

    count = Size(data_key="count")
    r""" The number of host I/O queue pairs.


Example: 4 """

    depth = Size(data_key="depth")
    r""" The host I/O queue depth.


Example: 16 """

    @property
    def resource(self):
        return NvmeSubsystemIoQueueDefault

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


class NvmeSubsystemIoQueueDefault(Resource):

    _schema = NvmeSubsystemIoQueueDefaultSchema
