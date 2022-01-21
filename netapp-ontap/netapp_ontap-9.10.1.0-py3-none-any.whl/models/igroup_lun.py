r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IgroupLun", "IgroupLunSchema"]
__pdoc__ = {
    "IgroupLunSchema.resource": False,
    "IgroupLun": False,
}


class IgroupLunSchema(ResourceSchema):
    """The fields of the IgroupLun object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the igroup_lun. """

    name = fields.Str(data_key="name")
    r""" The name of the LUN.


Example: lun1 """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the igroup_lun. """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the LUN.


Example: 4ea7a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return IgroupLun

    gettable_fields = [
        "links",
        "name",
        "node.links",
        "node.name",
        "node.uuid",
        "uuid",
    ]
    """links,name,node.links,node.name,node.uuid,uuid,"""

    patchable_fields = [
        "node.name",
        "node.uuid",
    ]
    """node.name,node.uuid,"""

    postable_fields = [
        "node.name",
        "node.uuid",
    ]
    """node.name,node.uuid,"""


class IgroupLun(Resource):

    _schema = IgroupLunSchema
