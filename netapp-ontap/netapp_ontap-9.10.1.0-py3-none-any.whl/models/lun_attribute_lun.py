r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunAttributeLun", "LunAttributeLunSchema"]
__pdoc__ = {
    "LunAttributeLunSchema.resource": False,
    "LunAttributeLun": False,
}


class LunAttributeLunSchema(ResourceSchema):
    """The fields of the LunAttributeLun object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the lun_attribute_lun. """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the LUN.


Example: 4ea7a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return LunAttributeLun

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


class LunAttributeLun(Resource):

    _schema = LunAttributeLunSchema
