r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VdiOnNasHyperVAccess", "VdiOnNasHyperVAccessSchema"]
__pdoc__ = {
    "VdiOnNasHyperVAccessSchema.resource": False,
    "VdiOnNasHyperVAccess": False,
}


class VdiOnNasHyperVAccessSchema(ResourceSchema):
    """The fields of the VdiOnNasHyperVAccess object"""

    service_account = fields.Str(data_key="service_account")
    r""" Hyper-V service account. """

    @property
    def resource(self):
        return VdiOnNasHyperVAccess

    gettable_fields = [
        "service_account",
    ]
    """service_account,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "service_account",
    ]
    """service_account,"""


class VdiOnNasHyperVAccess(Resource):

    _schema = VdiOnNasHyperVAccessSchema
