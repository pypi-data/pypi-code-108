r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NvmeSubsystemHosts", "NvmeSubsystemHostsSchema"]
__pdoc__ = {
    "NvmeSubsystemHostsSchema.resource": False,
    "NvmeSubsystemHosts": False,
}


class NvmeSubsystemHostsSchema(ResourceSchema):
    """The fields of the NvmeSubsystemHosts object"""

    nqn = fields.Str(data_key="nqn")
    r""" The NVMe qualified name (NQN) used to identify the NVMe storage target.


Example: nqn.1992-01.example.com:string """

    @property
    def resource(self):
        return NvmeSubsystemHosts

    gettable_fields = [
        "nqn",
    ]
    """nqn,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "nqn",
    ]
    """nqn,"""


class NvmeSubsystemHosts(Resource):

    _schema = NvmeSubsystemHostsSchema
