r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NvmeSubsystemControllerAdminQueue", "NvmeSubsystemControllerAdminQueueSchema"]
__pdoc__ = {
    "NvmeSubsystemControllerAdminQueueSchema.resource": False,
    "NvmeSubsystemControllerAdminQueue": False,
}


class NvmeSubsystemControllerAdminQueueSchema(ResourceSchema):
    """The fields of the NvmeSubsystemControllerAdminQueue object"""

    depth = Size(data_key="depth")
    r""" The depth of the admin queue for the controller. """

    @property
    def resource(self):
        return NvmeSubsystemControllerAdminQueue

    gettable_fields = [
        "depth",
    ]
    """depth,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NvmeSubsystemControllerAdminQueue(Resource):

    _schema = NvmeSubsystemControllerAdminQueueSchema
