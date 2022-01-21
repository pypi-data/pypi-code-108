r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeConstituents", "VolumeConstituentsSchema"]
__pdoc__ = {
    "VolumeConstituentsSchema.resource": False,
    "VolumeConstituents": False,
}


class VolumeConstituentsSchema(ResourceSchema):
    """The fields of the VolumeConstituents object"""

    aggregates = fields.Nested("netapp_ontap.models.volume_aggregates.VolumeAggregatesSchema", unknown=EXCLUDE, data_key="aggregates")
    r""" The aggregates field of the volume_constituents. """

    movement = fields.Nested("netapp_ontap.models.volume_movement.VolumeMovementSchema", unknown=EXCLUDE, data_key="movement")
    r""" The movement field of the volume_constituents. """

    name = fields.Str(data_key="name")
    r""" FlexGroup Constituents name """

    space = fields.Nested("netapp_ontap.models.volume_space.VolumeSpaceSchema", unknown=EXCLUDE, data_key="space")
    r""" The space field of the volume_constituents. """

    @property
    def resource(self):
        return VolumeConstituents

    gettable_fields = [
        "aggregates",
        "movement",
        "name",
        "space",
    ]
    """aggregates,movement,name,space,"""

    patchable_fields = [
        "aggregates",
        "movement",
        "space",
    ]
    """aggregates,movement,space,"""

    postable_fields = [
        "aggregates",
        "movement",
        "space",
    ]
    """aggregates,movement,space,"""


class VolumeConstituents(Resource):

    _schema = VolumeConstituentsSchema
