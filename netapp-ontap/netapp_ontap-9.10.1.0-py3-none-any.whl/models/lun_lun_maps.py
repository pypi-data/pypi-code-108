r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunLunMaps", "LunLunMapsSchema"]
__pdoc__ = {
    "LunLunMapsSchema.resource": False,
    "LunLunMaps": False,
}


class LunLunMapsSchema(ResourceSchema):
    """The fields of the LunLunMaps object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the lun_lun_maps. """

    igroup = fields.Nested("netapp_ontap.models.lun_igroup.LunIgroupSchema", unknown=EXCLUDE, data_key="igroup")
    r""" The igroup field of the lun_lun_maps. """

    logical_unit_number = Size(data_key="logical_unit_number")
    r""" The logical unit number assigned to the LUN for initiators in the initiator group. """

    @property
    def resource(self):
        return LunLunMaps

    gettable_fields = [
        "links",
        "igroup",
        "logical_unit_number",
    ]
    """links,igroup,logical_unit_number,"""

    patchable_fields = [
        "igroup",
    ]
    """igroup,"""

    postable_fields = [
        "igroup",
    ]
    """igroup,"""


class LunLunMaps(Resource):

    _schema = LunLunMapsSchema
