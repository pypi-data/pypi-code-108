r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ZappNvmeComponentsSubsystemHosts", "ZappNvmeComponentsSubsystemHostsSchema"]
__pdoc__ = {
    "ZappNvmeComponentsSubsystemHostsSchema.resource": False,
    "ZappNvmeComponentsSubsystemHosts": False,
}


class ZappNvmeComponentsSubsystemHostsSchema(ResourceSchema):
    """The fields of the ZappNvmeComponentsSubsystemHosts object"""

    nqn = fields.Str(data_key="nqn")
    r""" The host NQN. """

    @property
    def resource(self):
        return ZappNvmeComponentsSubsystemHosts

    gettable_fields = [
        "nqn",
    ]
    """nqn,"""

    patchable_fields = [
        "nqn",
    ]
    """nqn,"""

    postable_fields = [
        "nqn",
    ]
    """nqn,"""


class ZappNvmeComponentsSubsystemHosts(Resource):

    _schema = ZappNvmeComponentsSubsystemHostsSchema
