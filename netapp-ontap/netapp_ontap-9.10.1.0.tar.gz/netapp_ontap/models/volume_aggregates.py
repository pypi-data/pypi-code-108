r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeAggregates", "VolumeAggregatesSchema"]
__pdoc__ = {
    "VolumeAggregatesSchema.resource": False,
    "VolumeAggregates": False,
}


class VolumeAggregatesSchema(ResourceSchema):
    """The fields of the VolumeAggregates object"""

    name = fields.Str(data_key="name")
    r""" Name of the aggregate hosting the FlexGroup Constituent. """

    uuid = fields.Str(data_key="uuid")
    r""" Unique identifier for the aggregate.

Example: 028baa66-41bd-11e9-81d5-00a0986138f7 """

    @property
    def resource(self):
        return VolumeAggregates

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


class VolumeAggregates(Resource):

    _schema = VolumeAggregatesSchema
