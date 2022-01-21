r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IgroupChild", "IgroupChildSchema"]
__pdoc__ = {
    "IgroupChildSchema.resource": False,
    "IgroupChild": False,
}


class IgroupChildSchema(ResourceSchema):
    """The fields of the IgroupChild object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the igroup_child. """

    comment = fields.Str(data_key="comment")
    r""" A comment available for use by the administrator. """

    igroups = fields.List(fields.Nested("netapp_ontap.models.igroup_child.IgroupChildSchema", unknown=EXCLUDE), data_key="igroups")
    r""" Further nested initiator groups. """

    name = fields.Str(data_key="name")
    r""" The name of the initiator group.


Example: igroup1 """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the initiator group.


Example: 4ea7a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return IgroupChild

    gettable_fields = [
        "links",
        "comment",
        "igroups",
        "name",
        "uuid",
    ]
    """links,comment,igroups,name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""


class IgroupChild(Resource):

    _schema = IgroupChildSchema
