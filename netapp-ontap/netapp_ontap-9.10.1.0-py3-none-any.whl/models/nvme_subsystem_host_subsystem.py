r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NvmeSubsystemHostSubsystem", "NvmeSubsystemHostSubsystemSchema"]
__pdoc__ = {
    "NvmeSubsystemHostSubsystemSchema.resource": False,
    "NvmeSubsystemHostSubsystem": False,
}


class NvmeSubsystemHostSubsystemSchema(ResourceSchema):
    """The fields of the NvmeSubsystemHostSubsystem object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the nvme_subsystem_host_subsystem. """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the NVMe subsystem.


Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return NvmeSubsystemHostSubsystem

    gettable_fields = [
        "links",
        "uuid",
    ]
    """links,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NvmeSubsystemHostSubsystem(Resource):

    _schema = NvmeSubsystemHostSubsystemSchema
