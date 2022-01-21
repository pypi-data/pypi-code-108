r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunAttributes", "LunAttributesSchema"]
__pdoc__ = {
    "LunAttributesSchema.resource": False,
    "LunAttributes": False,
}


class LunAttributesSchema(ResourceSchema):
    """The fields of the LunAttributes object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the lun_attributes. """

    name = fields.Str(data_key="name")
    r""" The attribute name.


Example: name1 """

    value = fields.Str(data_key="value")
    r""" The attribute value.


Example: value1 """

    @property
    def resource(self):
        return LunAttributes

    gettable_fields = [
        "links",
        "name",
        "value",
    ]
    """links,name,value,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "name",
        "value",
    ]
    """name,value,"""


class LunAttributes(Resource):

    _schema = LunAttributesSchema
