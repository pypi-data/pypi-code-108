r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["RaidGroupReconstruct", "RaidGroupReconstructSchema"]
__pdoc__ = {
    "RaidGroupReconstructSchema.resource": False,
    "RaidGroupReconstruct": False,
}


class RaidGroupReconstructSchema(ResourceSchema):
    """The fields of the RaidGroupReconstruct object"""

    active = fields.Boolean(data_key="active")
    r""" One or more disks in this RAID group are being reconstructed. """

    percent = Size(data_key="percent")
    r""" Reconstruct percentage

Example: 10 """

    @property
    def resource(self):
        return RaidGroupReconstruct

    gettable_fields = [
        "active",
        "percent",
    ]
    """active,percent,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class RaidGroupReconstruct(Resource):

    _schema = RaidGroupReconstructSchema
