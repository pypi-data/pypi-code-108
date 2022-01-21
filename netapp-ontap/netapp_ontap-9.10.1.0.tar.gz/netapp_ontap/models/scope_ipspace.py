r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ScopeIpspace", "ScopeIpspaceSchema"]
__pdoc__ = {
    "ScopeIpspaceSchema.resource": False,
    "ScopeIpspace": False,
}


class ScopeIpspaceSchema(ResourceSchema):
    """The fields of the ScopeIpspace object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the scope_ipspace. """

    name = fields.Str(data_key="name")
    r""" IPspace name

Example: exchange """

    uuid = fields.Str(data_key="uuid")
    r""" IPspace UUID

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return ScopeIpspace

    gettable_fields = [
        "links",
        "name",
        "uuid",
    ]
    """links,name,uuid,"""

    patchable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    postable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""


class ScopeIpspace(Resource):

    _schema = ScopeIpspaceSchema
