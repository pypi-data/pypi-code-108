r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IgroupParent", "IgroupParentSchema"]
__pdoc__ = {
    "IgroupParentSchema.resource": False,
    "IgroupParent": False,
}


class IgroupParentSchema(ResourceSchema):
    """The fields of the IgroupParent object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the igroup_parent. """

    comment = fields.Str(data_key="comment")
    r""" A comment available for use by the administrator. """

    name = fields.Str(data_key="name")
    r""" The name of the initiator group.


Example: igroup1 """

    parent_igroups = fields.List(fields.Nested("netapp_ontap.models.igroup_parent.IgroupParentSchema", unknown=EXCLUDE), data_key="parent_igroups")
    r""" The initiator groups that contain this initiator group as as member. """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the initiator group.


Example: 4ea7a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return IgroupParent

    gettable_fields = [
        "links",
        "comment",
        "name",
        "parent_igroups",
        "uuid",
    ]
    """links,comment,name,parent_igroups,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class IgroupParent(Resource):

    _schema = IgroupParentSchema
