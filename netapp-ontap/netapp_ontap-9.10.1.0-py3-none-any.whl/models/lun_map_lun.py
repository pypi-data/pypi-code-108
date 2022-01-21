r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunMapLun", "LunMapLunSchema"]
__pdoc__ = {
    "LunMapLunSchema.resource": False,
    "LunMapLun": False,
}


class LunMapLunSchema(ResourceSchema):
    """The fields of the LunMapLun object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the lun_map_lun. """

    name = fields.Str(data_key="name")
    r""" The fully qualified path name of the LUN composed of a \"/vol\" prefix, the volume name, the (optional) qtree name, and file name of the LUN. Valid in POST.


Example: /vol/volume1/qtree1/lun1 """

    node = fields.Nested("netapp_ontap.models.lun_map_lun_node.LunMapLunNodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the lun_map_lun. """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the LUN. Valid in POST.


Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return LunMapLun

    gettable_fields = [
        "links",
        "name",
        "node",
        "uuid",
    ]
    """links,name,node,uuid,"""

    patchable_fields = [
        "node",
    ]
    """node,"""

    postable_fields = [
        "name",
        "node",
        "uuid",
    ]
    """name,node,uuid,"""


class LunMapLun(Resource):

    _schema = LunMapLunSchema
