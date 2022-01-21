r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SvmMigrationDestination", "SvmMigrationDestinationSchema"]
__pdoc__ = {
    "SvmMigrationDestinationSchema.resource": False,
    "SvmMigrationDestination": False,
}


class SvmMigrationDestinationSchema(ResourceSchema):
    """The fields of the SvmMigrationDestination object"""

    ipspace = fields.Nested("netapp_ontap.resources.ipspace.IpspaceSchema", unknown=EXCLUDE, data_key="ipspace")
    r""" The ipspace field of the svm_migration_destination. """

    volume_placement = fields.Nested("netapp_ontap.models.svm_migration_volume_placement.SvmMigrationVolumePlacementSchema", unknown=EXCLUDE, data_key="volume_placement")
    r""" The volume_placement field of the svm_migration_destination. """

    @property
    def resource(self):
        return SvmMigrationDestination

    gettable_fields = [
        "ipspace.links",
        "ipspace.name",
        "ipspace.uuid",
        "volume_placement",
    ]
    """ipspace.links,ipspace.name,ipspace.uuid,volume_placement,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "ipspace.name",
        "ipspace.uuid",
        "volume_placement",
    ]
    """ipspace.name,ipspace.uuid,volume_placement,"""


class SvmMigrationDestination(Resource):

    _schema = SvmMigrationDestinationSchema
