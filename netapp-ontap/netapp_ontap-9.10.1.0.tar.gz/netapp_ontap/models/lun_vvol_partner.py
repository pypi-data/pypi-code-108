r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunVvolPartner", "LunVvolPartnerSchema"]
__pdoc__ = {
    "LunVvolPartnerSchema.resource": False,
    "LunVvolPartner": False,
}


class LunVvolPartnerSchema(ResourceSchema):
    """The fields of the LunVvolPartner object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the lun_vvol_partner. """

    name = fields.Str(data_key="name")
    r""" The name of the partner LUN.


Example: /vol/vol1/lun1 """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the partner LUN.


Example: 4ea7a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return LunVvolPartner

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


class LunVvolPartner(Resource):

    _schema = LunVvolPartnerSchema
