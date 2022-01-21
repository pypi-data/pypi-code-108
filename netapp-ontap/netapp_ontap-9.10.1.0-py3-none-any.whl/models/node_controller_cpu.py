r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeControllerCpu", "NodeControllerCpuSchema"]
__pdoc__ = {
    "NodeControllerCpuSchema.resource": False,
    "NodeControllerCpu": False,
}


class NodeControllerCpuSchema(ResourceSchema):
    """The fields of the NodeControllerCpu object"""

    count = Size(data_key="count")
    r""" Number of CPUs on the node.

Example: 20 """

    firmware_release = fields.Str(data_key="firmware_release")
    r""" Firmware release number. Defined by the CPU manufacturer. """

    processor = fields.Str(data_key="processor")
    r""" CPU type on the node. """

    @property
    def resource(self):
        return NodeControllerCpu

    gettable_fields = [
        "count",
        "firmware_release",
        "processor",
    ]
    """count,firmware_release,processor,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NodeControllerCpu(Resource):

    _schema = NodeControllerCpuSchema
