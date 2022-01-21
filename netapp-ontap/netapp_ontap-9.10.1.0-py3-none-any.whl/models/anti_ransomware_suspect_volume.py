r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AntiRansomwareSuspectVolume", "AntiRansomwareSuspectVolumeSchema"]
__pdoc__ = {
    "AntiRansomwareSuspectVolumeSchema.resource": False,
    "AntiRansomwareSuspectVolume": False,
}


class AntiRansomwareSuspectVolumeSchema(ResourceSchema):
    """The fields of the AntiRansomwareSuspectVolume object"""

    name = fields.Str(data_key="name")
    r""" The name field of the anti_ransomware_suspect_volume. """

    uuid = fields.Str(data_key="uuid")
    r""" The uuid field of the anti_ransomware_suspect_volume. """

    @property
    def resource(self):
        return AntiRansomwareSuspectVolume

    gettable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    patchable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    postable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""


class AntiRansomwareSuspectVolume(Resource):

    _schema = AntiRansomwareSuspectVolumeSchema
