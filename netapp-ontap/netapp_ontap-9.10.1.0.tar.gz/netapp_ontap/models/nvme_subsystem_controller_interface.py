r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NvmeSubsystemControllerInterface", "NvmeSubsystemControllerInterfaceSchema"]
__pdoc__ = {
    "NvmeSubsystemControllerInterfaceSchema.resource": False,
    "NvmeSubsystemControllerInterface": False,
}


class NvmeSubsystemControllerInterfaceSchema(ResourceSchema):
    """The fields of the NvmeSubsystemControllerInterface object"""

    name = fields.Str(data_key="name")
    r""" The name of the logical interface.


Example: lif1 """

    transport_address = fields.Str(data_key="transport_address")
    r""" The transport address of the logical interface.


Example: nn-0x200400a0989a1c8d:pn-0x200500a0989a1c8d """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the logical interface.


Example: fa1c5941-2593-11e9-94c4-00a0989a1c8e """

    @property
    def resource(self):
        return NvmeSubsystemControllerInterface

    gettable_fields = [
        "name",
        "transport_address",
        "uuid",
    ]
    """name,transport_address,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NvmeSubsystemControllerInterface(Resource):

    _schema = NvmeSubsystemControllerInterfaceSchema
