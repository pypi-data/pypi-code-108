r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeFlexgroup", "VolumeFlexgroupSchema"]
__pdoc__ = {
    "VolumeFlexgroupSchema.resource": False,
    "VolumeFlexgroup": False,
}


class VolumeFlexgroupSchema(ResourceSchema):
    """The fields of the VolumeFlexgroup object"""

    name = fields.Str(data_key="name")
    r""" Name of the FlexGroup volume that the constituent is part of.

Example: my_flexgroup """

    uuid = fields.Str(data_key="uuid")
    r""" Unique identifier for the FlexGroup volume that the constituent is part of.

Example: 75c9cfb0-3eb4-11eb-9fb4-005056bb088a """

    @property
    def resource(self):
        return VolumeFlexgroup

    gettable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class VolumeFlexgroup(Resource):

    _schema = VolumeFlexgroupSchema
