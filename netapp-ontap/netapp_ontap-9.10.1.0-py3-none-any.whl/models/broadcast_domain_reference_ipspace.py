r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["BroadcastDomainReferenceIpspace", "BroadcastDomainReferenceIpspaceSchema"]
__pdoc__ = {
    "BroadcastDomainReferenceIpspaceSchema.resource": False,
    "BroadcastDomainReferenceIpspace": False,
}


class BroadcastDomainReferenceIpspaceSchema(ResourceSchema):
    """The fields of the BroadcastDomainReferenceIpspace object"""

    name = fields.Str(data_key="name")
    r""" Name of the broadcast domain's IPspace

Example: ipspace1 """

    @property
    def resource(self):
        return BroadcastDomainReferenceIpspace

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class BroadcastDomainReferenceIpspace(Resource):

    _schema = BroadcastDomainReferenceIpspaceSchema
