r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SvmMigrationVolumePlacement", "SvmMigrationVolumePlacementSchema"]
__pdoc__ = {
    "SvmMigrationVolumePlacementSchema.resource": False,
    "SvmMigrationVolumePlacement": False,
}


class SvmMigrationVolumePlacementSchema(ResourceSchema):
    """The fields of the SvmMigrationVolumePlacement object"""

    aggregates = fields.List(fields.Nested("netapp_ontap.resources.aggregate.AggregateSchema", unknown=EXCLUDE), data_key="aggregates")
    r""" Optional property used to specify the list of desired aggregates to use for volume creation in the destination. """

    @property
    def resource(self):
        return SvmMigrationVolumePlacement

    gettable_fields = [
        "aggregates.links",
        "aggregates.name",
        "aggregates.uuid",
    ]
    """aggregates.links,aggregates.name,aggregates.uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "aggregates.name",
        "aggregates.uuid",
    ]
    """aggregates.name,aggregates.uuid,"""


class SvmMigrationVolumePlacement(Resource):

    _schema = SvmMigrationVolumePlacementSchema
