r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SvmMigrationSource", "SvmMigrationSourceSchema"]
__pdoc__ = {
    "SvmMigrationSourceSchema.resource": False,
    "SvmMigrationSource": False,
}


class SvmMigrationSourceSchema(ResourceSchema):
    """The fields of the SvmMigrationSource object"""

    cluster = fields.Nested("netapp_ontap.resources.cluster.ClusterSchema", unknown=EXCLUDE, data_key="cluster")
    r""" The cluster field of the svm_migration_source. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", unknown=EXCLUDE, data_key="svm")
    r""" The svm field of the svm_migration_source. """

    @property
    def resource(self):
        return SvmMigrationSource

    gettable_fields = [
        "cluster.links",
        "cluster.name",
        "cluster.uuid",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """cluster.links,cluster.name,cluster.uuid,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "cluster.name",
        "cluster.uuid",
        "svm.name",
        "svm.uuid",
    ]
    """cluster.name,cluster.uuid,svm.name,svm.uuid,"""


class SvmMigrationSource(Resource):

    _schema = SvmMigrationSourceSchema
