r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunConsistencyGroup", "LunConsistencyGroupSchema"]
__pdoc__ = {
    "LunConsistencyGroupSchema.resource": False,
    "LunConsistencyGroup": False,
}


class LunConsistencyGroupSchema(ResourceSchema):
    """The fields of the LunConsistencyGroup object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the lun_consistency_group. """

    name = fields.Str(data_key="name")
    r""" The name of the consistency group.


Example: cg1 """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the consistency group.


Example: 4abc2317-4332-9d37-93a0-20bd29c22df0 """

    @property
    def resource(self):
        return LunConsistencyGroup

    gettable_fields = [
        "links",
        "name",
        "uuid",
    ]
    """links,name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class LunConsistencyGroup(Resource):

    _schema = LunConsistencyGroupSchema
