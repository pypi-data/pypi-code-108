r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IgroupLunMaps", "IgroupLunMapsSchema"]
__pdoc__ = {
    "IgroupLunMapsSchema.resource": False,
    "IgroupLunMaps": False,
}


class IgroupLunMapsSchema(ResourceSchema):
    """The fields of the IgroupLunMaps object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the igroup_lun_maps. """

    logical_unit_number = Size(data_key="logical_unit_number")
    r""" The logical unit number assigned to the LUN for initiators in the initiator group. """

    lun = fields.Nested("netapp_ontap.models.igroup_lun.IgroupLunSchema", unknown=EXCLUDE, data_key="lun")
    r""" The lun field of the igroup_lun_maps. """

    @property
    def resource(self):
        return IgroupLunMaps

    gettable_fields = [
        "links",
        "logical_unit_number",
        "lun",
    ]
    """links,logical_unit_number,lun,"""

    patchable_fields = [
        "lun",
    ]
    """lun,"""

    postable_fields = [
        "lun",
    ]
    """lun,"""


class IgroupLunMaps(Resource):

    _schema = IgroupLunMapsSchema
